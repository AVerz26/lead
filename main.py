# main.py
import streamlit as st
import pandas as pd
import requests
import re
import time
import ast

# tenta importar client oficial; se não existir, usaremos requests direto
try:
    from serpapi import GoogleSearch
    SERPAPI_CLIENT_AVAILABLE = True
except Exception:
    SERPAPI_CLIENT_AVAILABLE = False

st.set_page_config(page_title="Lead Finder", layout="wide")
st.title("🕵️‍♂️ Buscador de Leads")

SERPAPI_KEY = st.text_input("Insira o seu SerpApi API Key", type="password")

if SERPAPI_KEY:
    area = st.text_input("Área de atuação (ex: advogado, imobiliária)")
    cidade = st.text_input("Cidade (ex: Piracicaba, São Paulo)")
    num_resultados = st.number_input("Número de resultados (máx 200)", min_value=1, max_value=200, value=20)
    delay = st.number_input("Delay entre requests (s)", min_value=0.0, max_value=5.0, value=1.0)
else:
    st.info("Por favor, insira a sua SerpApi API Key para continuar.")

def serpapi_search(params, api_key):
    """Faz a requisição à SerpApi: usa o client se disponível ou requests direto."""
    params = dict(params)
    params["api_key"] = api_key
    if SERPAPI_CLIENT_AVAILABLE:
        # client oficial
        search = GoogleSearch(params)
        return search.get_dict()
    else:
        # fallback HTTP
        resp = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

def _parse_coords(raw):
    """Normaliza coordenadas: aceita dict ou string JSON; retorna dict com keys 'latitude','longitude' ou None."""
    if not raw:
        return None
    if isinstance(raw, dict):
        return raw
    # se for string parecido com dict/json
    try:
        parsed = ast.literal_eval(str(raw))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        try:
            parsed = requests.utils.json.loads(str(raw))
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
    return None

def buscar_leads(area, cidade, num_resultados, api_key):
    """
    Faz paginação e retorna DataFrame com os resultados agregados.
    Cada página tenta buscar com start = i*20 (aprox 20 por página).
    """
    query = f"{area} em {cidade}"
    dados = []
    pagina = 0
    per_page = 20
    while len(dados) < num_resultados:
        params = {
            "q": query,
            "engine": "google_maps",
            "google_domain": "google.com.br",  # opcional
            "hl": "pt",
            "gl": "br",
            "start": pagina * per_page  # paginação: 0, 20, 40...
        }
        try:
            resp = serpapi_search(params, api_key)
        except Exception as e:
            st.error(f"Erro na chamada à SerpApi: {e}")
            break

        leads = resp.get("local_results") or resp.get("local_results", []) or []
        # em alguns responses o campo pode ter outro nome; tenta outros caminhos
        if not leads:
            # tenta procurar em 'local_results' ou 'local_results' (fallback)
            leads = resp.get("local_results") or resp.get("local_results", []) or []

        if not leads:
            # se não veio nada, para a paginação
            break

        for lead in leads:
            gps_raw = lead.get("gps_coordinates") or lead.get("gps") or lead.get("coordinates") or None
            gps = _parse_coords(gps_raw)
            dados.append({
                "nome": lead.get("title"),
                "telefone": lead.get("phone"),
                "site": lead.get("website"),
                "endereco": lead.get("address"),
                "rating": lead.get("rating"),
                "avaliacoes": lead.get("reviews"),
                "coordenadas": gps
            })
            if len(dados) >= num_resultados:
                break

        pagina += 1
        time.sleep(1)  # pequeno sleep entre páginas para não sobrecarregar

        # segurança: limite máximo de páginas
        if pagina > 10:
            break

    df = pd.DataFrame(dados[:num_resultados])
    for col in ["site", "telefone", "endereco"]:
        if col not in df.columns:
            df[col] = None
    return df

def extrair_emails_do_site(url):
    if not url:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        return ", ".join(sorted(set(emails))) if emails else None
    except Exception:
        return None

def extrair_linkedin_do_site(url):
    if not url:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible)"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text
        links = re.findall(r'https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9_/.-]+', html)
        return ", ".join(sorted(set(links))) if links else None
    except Exception:
        return None

def gerar_dataframe_completo(area, cidade, num_resultados, api_key, delay=1.0):
    df = buscar_leads(area, cidade, num_resultados, api_key)
    if df.empty:
        return df

    emails = []
    linkedins = []
    lats = []
    lons = []

    # itera por todas as linhas (seguro mesmo que falte site/coordenadas)
    for row in df.itertuples(index=False):
        site = getattr(row, "site", None)
        coords = getattr(row, "coordenadas", None)
        emails.append(extrair_emails_do_site(site))
        linkedins.append(extrair_linkedin_do_site(site))
        coords_parsed = _parse_coords(coords)
        if coords_parsed:
            lat = coords_parsed.get("latitude") or coords_parsed.get("lat") or coords_parsed.get("y") or None
            lon = coords_parsed.get("longitude") or coords_parsed.get("lng") or coords_parsed.get("x") or None
            lats.append(lat)
            lons.append(lon)
        else:
            lats.append(None)
            lons.append(None)
        time.sleep(delay)

    df = df.reset_index(drop=True)
    df["emails"] = emails
    df["linkedin"] = linkedins
    df["lat"] = pd.to_numeric(lats, errors="coerce")
    df["lon"] = pd.to_numeric(lons, errors="coerce")
    return df

# Botão para buscar
if SERPAPI_KEY and st.button("🔍 Buscar Leads"):
    if not area or not cidade:
        st.warning("Por favor, preencha área e cidade.")
    else:
        with st.spinner("Buscando leads..."):
            df_leads = gerar_dataframe_completo(area, cidade, num_resultados=int(num_resultados), api_key=SERPAPI_KEY, delay=float(delay))
            if df_leads.empty:
                st.info("Nenhum lead encontrado para os critérios informados.")
            else:
                st.success(f"{len(df_leads)} leads encontrados!")
                st.dataframe(df_leads)

                mapa_df = df_leads.dropna(subset=["lat", "lon"])
                if not mapa_df.empty:
                    # st.map requer colunas lat & lon (ou latitude/longitude); passamos lat/lon
                    st.map(mapa_df[["lat", "lon"]])

import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests
import re
import time
import ast 


st.set_page_config(page_title="Lead Finder", layout="wide")

st.title("🕵️‍♂️ Buscador de Leads")

SERPAPI_KEY = st.text_input("Insira o seu SerpApi API Key", type="password")

if SERPAPI_KEY:

  # Inputs do usuário
  area = st.text_input("Área de atuação (ex: advogado, imobiliária)")
  cidade = st.text_input("Cidade (ex: Piracicaba, São Paulo)")
  radius = st.number_input("Raio em metros (não usado diretamente pelo Google Maps)", value=10000)
  
  num_resultados = st.number_input("Número de resultados", min_value=1, max_value=100, value=20)
  delay = 1

else:
  st.info("Por favor, insira a sua SerpApi API Key para continuar.")

def buscar_leads(area, cidade, num_resultados, api_key):
    """
    Consulta o Google Maps via SerpApi e retorna leads básicos,
    iterando até alcançar num_resultados (aprox. 20 resultados por página).
    """
    query = f"{area} em {cidade}"
    dados = []

    # Cada página do SerpApi traz até 20 resultados
    paginas = (num_resultados // 20) + 1

    for i in range(paginas):
        search = GoogleSearch({
            "q": query,
            "engine": "google_maps",
            "google_domain": "google.com.br",
            "hl": "pt",
            "gl": "br",
            "start": i * 20,
            "api_key": api_key
        })

        resultados = search.get_dict()
        leads = resultados.get("local_results", [])

        if not leads:  # se não vier nada, para pra não gastar crédito
            break

        for lead in leads:
            dados.append({
                "nome": lead.get("title"),
                "telefone": lead.get("phone"),
                "site": lead.get("website"),
                "endereco": lead.get("address"),
                "rating": lead.get("rating"),
                "avaliacoes": lead.get("reviews"),
                "coordenadas": lead.get("gps_coordinates")
            })

        # Se já bateu a quantidade pedida, para
        if len(dados) >= num_resultados:
            break

    # monta dataframe
    df = pd.DataFrame(dados[:num_resultados])

    # garante colunas principais
    for col in ["site", "telefone", "endereco"]:
        if col not in df.columns:
            df[col] = None

    return df


def extrair_emails_do_site(url):
    if not url:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        emails = list(set(emails))
        return ", ".join(emails) if emails else None
    except:
        return None

def extrair_linkedin_do_site(url):
    if not url:
        return None
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text
        linkedin_links = re.findall(r'https?://(?:www\.)?linkedin\.com/[a-zA-Z0-9_/.-]+', html)
        linkedin_links = list(set(linkedin_links))
        return ", ".join(linkedin_links) if linkedin_links else None
    except:
        return None

def gerar_dataframe_completo(area, cidade, num_resultados, api_key, delay=1):
    df = buscar_leads(area, cidade, num_resultados, api_key)
    emails = []
    linkedin = []
    lats = []
    lons = []
    for site, coords in zip(df.get("site", []), df.get("coordenadas", [])):
        emails.append(extrair_emails_do_site(site))
        linkedin.append(extrair_linkedin_do_site(site))
        if coords:
            lats.append(coords.get("lat"))
            lons.append(coords.get("lng"))
        else:
            lats.append(None)
            lons.append(None)
        time.sleep(delay)
    df["emails"] = emails
    df["linkedin"] = linkedin
    df["latitude"] = lats
    df["longitude"] = lons
    return df

# Botão para buscar
if st.button("🔍 Buscar Leads"):
    if not area or not cidade or not SERPAPI_KEY:
        st.warning("Por favor, preencha todos os campos!")
    else:
        with st.spinner("Buscando leads..."):
            df_leads = gerar_dataframe_completo(area, cidade, num_resultados, SERPAPI_KEY)
            if df_leads.empty:
                st.info("Nenhum lead encontrado para os critérios informados.")
            else:
                st.success(f"{len(df_leads)} leads encontrados!")
                st.dataframe(df_leads)
                

                if not df.empty:
                    # garante que coordenadas seja dicionário
                    df["coordenadas"] = df["coordenadas"].apply(lambda x: ast.literal_eval(str(x)) if x else {})
                    
                    # cria colunas separadas
                    df["latitude"] = df["coordenadas"].apply(lambda x: x.get("latitude"))
                    df["longitude"] = df["coordenadas"].apply(lambda x: x.get("longitude"))
                    
                    # agora pode mandar pro mapa
                    st.map(df[["latitude", "longitude"]])

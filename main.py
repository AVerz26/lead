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

def buscar_leads(area, cidade, num_resultados, api_key, delay=2):
    """
    Consulta o Google Maps via SerpApi e retorna leads básicos com paginação.
    """
    query = f"{area} em {cidade}"
    per_page = 20
    dados = []

    for starti in range(0, num_resultados, per_page):
        params = {
            "q": query,
            "engine": "google_maps",
            "type": "search",
            "hl": "pt",
            "gl": "br",
            "start": starti,
            "api_key": api_key
        }

        search = GoogleSearch(params)
        resultados = search.get_dict()
        leads = resultados.get("local_results", [])

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

        time.sleep(delay)  # evita bloqueio na API

    df = pd.DataFrame(dados)

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
            df_leads = gerar_dataframe_completo(area, cidade, num_resultados, SERPAPI_KEY, delay)
            if df_leads.empty:
                st.info("Nenhum lead encontrado para os critérios informados.")
            else:
                st.success(f"{len(df_leads)} leads encontrados!")
                st.dataframe(df_leads)
                
                # garante que coordenadas seja dicionário
                df_leads["coordenadas"] = df_leads["coordenadas"].apply(
                    lambda x: ast.literal_eval(str(x)) if x else {}
                )
                
                # cria colunas separadas
                df_leads["latitude"] = df_leads["coordenadas"].apply(lambda x: x.get("latitude"))
                df_leads["longitude"] = df_leads["coordenadas"].apply(lambda x: x.get("longitude"))
                
                # Mostra mapa só com os que têm coordenadas
                mapa_df = df_leads.dropna(subset=["latitude", "longitude"])
                if not mapa_df.empty:
                    st.map(mapa_df[["latitude", "longitude"]])

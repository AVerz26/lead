import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests
import re
import time
import ast


st.set_page_config(page_title="Leads Finder", layout="wide")

st.title("Leads Finder App")

SERPAPI_KEY = st.text_input("SerpApi API Key", type="password")

if SERPAPI_KEY:

  # Inputs do usuário
  area = st.text_input("Area (Lawyer, Real Estate..)")
  cidade = st.text_input("City (ex: Brasilia, Miami..)")
  radius = st.number_input("Radius (km)", value=10)

  radius = radius * 1000
  
  num_resultados = 20
  delay = 1

else:
  st.info("Please, insert your SerpApi API Key to continue.")

def buscar_leads(area, cidade, num_resultados, api_key, delay=2):

    query = f"{area} em {cidade}"
    per_page = 20
    dados = []

    for starti in range(0, num_resultados, per_page):
        params = {
            "q": query,
            "engine": "google_maps",
            "google_domain": "google.com.br",
            "hl": "pt",
            "gl": "br",
            "api_key": api_key
        }

        search = GoogleSearch(params)
        resultados = search.get_dict()
        leads = resultados.get("local_results", [])

        for lead in leads:
            dados.append({
                "name": lead.get("title"),
                "phone": lead.get("phone"),
                "site": lead.get("website"),
                "address": lead.get("address"),
                "rating": lead.get("rating"),
                "reviews": lead.get("reviews"),
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
if st.button("Search Leads"):
    if not area or not cidade or not SERPAPI_KEY:
        st.warning("Please, fill in all fields!")
    else:
        with st.spinner("Searching leads..."):
            df_leads = gerar_dataframe_completo(area, cidade, num_resultados, SERPAPI_KEY, delay)
            if df_leads.empty:
                st.info("No leads found.")
            else:
                st.success(f"{len(df_leads)} leads founded!")
                v = df_leads.copy()
                v = v.drop(columns=["latitude", "longitude", "coordenadas"])
                st.dataframe(v)
                
                # garante que coordenadas seja dicionário
                df_leads["coordenadas"] = df_leads["coordenadas"].apply(
                    lambda x: ast.literal_eval(str(x)) if x else {}
                )
                
                # cria colunas separadas
                df_leads["latitude"] = df_leads["coordenadas"].apply(lambda x: x.get("latitude"))
                df_leads["longitude"] = df_leads["coordenadas"].apply(lambda x: x.get("longitude"))
                

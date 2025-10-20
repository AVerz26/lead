import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Multi-Level Radial Chart - Meio Círculo")

# Dados de exemplo com percentuais
data = pd.DataFrame({
    "Level1": ["Fruits", "Fruits", "Vegetables", "Vegetables", "Fruits", "Vegetables"],
    "Level2": ["Citrus", "Berries", "Leafy", "Root", "Tropical", "Stem"],
    "Level3": ["Orange", "Strawberry", "Spinach", "Carrot", "Mango", "Asparagus"],
    "Value": [20, 30, 25, 10, 15, 5]  # percentuais
})

# Criando gráfico sunburst
fig = go.Figure(go.Sunburst(
    labels=data['Level3'],  # rótulos do nível mais interno
    parents=data['Level2'],  # nível intermediário
    values=data['Value'],
    branchvalues="total",
    maxdepth=3,  # limita a 3 níveis
    hoverinfo="label+percent parent+percent entry",
    textinfo="label+percent parent",
))

# Conectando o nível 2 ao nível 1
fig.update_traces(
    labels=list(data['Level1']) + list(data['Level2']) + list(data['Level3']),
    parents=[""]*len(data['Level1']) + list(data['Level1']) + list(data['Level2']),
)

# Ajustando para meio círculo
fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
    sunburstcolorway=["#636efa","#ef553b","#00cc96","#ab63fa","#ffa15a","#19d3f3"],
    extendsunburstcolors=True,
    uniformtext=dict(minsize=10, mode='hide'),
    sunburst=dict(
        startangle=180,  # inicia do lado esquerdo
        endangle=360     # termina no lado direito
    )
)

st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("Multi-Level Radial Chart - Meio Círculo")

# Dados de exemplo com percentuais
data = pd.DataFrame({
    "Level1": ["Fruits", "Fruits", "Vegetables", "Vegetables", "Fruits", "Vegetables"],
    "Level2": ["Citrus", "Berries", "Leafy", "Root", "Tropical", "Stem"],
    "Level3": ["Orange", "Strawberry", "Spinach", "Carrot", "Mango", "Asparagus"],
    "Value": [20, 30, 25, 10, 15, 5]
})

# Preparando labels e parents
labels = list(data['Level1'].unique()) + list(data['Level2']) + list(data['Level3'])
parents = [""]*len(data['Level1'].unique()) + list(data['Level1']) + list(data['Level2'])
values = [0]*len(data['Level1'].unique()) + list(data['Value']) + list(data['Value'])  # placeholder

# Criando gráfico sunburst
fig = go.Figure(go.Sunburst(
    labels=labels,
    parents=parents,
    values=values,
    branchvalues="total",
    maxdepth=3,
    hoverinfo="label+percent parent",
    textinfo="label+percent parent",
    rotation=180  # inicia do lado esquerdo (meio círculo)
))

fig.update_traces(
    insidetextorientation='radial'
)

fig.update_layout(
    margin=dict(t=0, l=0, r=0, b=0),
)

st.plotly_chart(fig, use_container_width=True)

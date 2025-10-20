import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Multi-Level Radial Chart Example")

# Dados de exemplo
data = pd.DataFrame({
    "Level1": ["Fruits", "Fruits", "Vegetables", "Vegetables", "Fruits", "Vegetables"],
    "Level2": ["Citrus", "Berries", "Leafy", "Root", "Tropical", "Stem"],
    "Category": ["Orange", "Strawberry", "Spinach", "Carrot", "Mango", "Asparagus"],
    "Value": [10, 15, 12, 8, 7, 5]
})

# Criando gráfico sunburst (multi-level radial chart)
fig = px.sunburst(
    data,
    path=['Level1', 'Level2', 'Category'],  # define os níveis
    values='Value',
    color='Level1',  # cores pelo nível principal
    title="Multi-Level Radial Chart"
)

st.plotly_chart(fig)

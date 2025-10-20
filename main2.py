import streamlit as st
import plotly.graph_objects as go

st.title("Multi-Level Radial Chart - Meio Círculo")

# Dados de exemplo
level1_labels = ["Fruits", "Vegetables"]
level1_values = [50, 50]

level2_labels = ["Citrus", "Berries", "Leafy", "Root", "Tropical", "Stem"]
level2_values = [20, 30, 25, 10, 15, 5]

level3_labels = ["Orange", "Strawberry", "Spinach", "Carrot", "Mango", "Asparagus"]
level3_values = [10, 10, 15, 10, 5, 5]

# Cria gráfico tipo donut para cada nível
fig = go.Figure()

# Nível 1
fig.add_trace(go.Pie(
    labels=level1_labels,
    values=level1_values,
    hole=0.6,
    direction='clockwise',
    sort=False,
    rotation=180,  # meio círculo
    textinfo='label+percent',
    domain={'x':[0,1],'y':[0,1]}
))

# Nível 2
fig.add_trace(go.Pie(
    labels=level2_labels,
    values=level2_values,
    hole=0.4,
    direction='clockwise',
    sort=False,
    rotation=180,
    textinfo='label+percent',
    domain={'x':[0,1],'y':[0,1]}
))

# Nível 3
fig.add_trace(go.Pie(
    labels=level3_labels,
    values=level3_values,
    hole=0.2,
    direction='clockwise',
    sort=False,
    rotation=180,
    textinfo='label+percent',
    domain={'x':[0,1],'y':[0,1]}
))

fig.update_layout(margin=dict(t=0,l=0,r=0,b=0), showlegend=True)

st.plotly_chart(fig, use_container_width=True)

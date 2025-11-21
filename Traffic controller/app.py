import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

st.set_page_config(page_title="Traffic Optimizer", layout="wide")

st.title("🚦 Traffic Light Optimization Dashboard")
st.write("Compare traffic delays **before** and **after** optimization using AI rules.")

# Sample data – replace with actual simulation results
x = np.arange(0, 10, 1)

delay_before = np.random.randint(30, 60, size=10)
delay_after = delay_before - np.random.randint(5, 20, size=10)

df = pd.DataFrame({
    "Time": x,
    "Delay Before": delay_before,
    "Delay After": delay_after
})

# Create beautiful Plotly chart
fig = px.line(
    df,
    x="Time",
    y=["Delay Before", "Delay After"],
    title="Traffic Delay Before vs After Optimization",
    markers=True,
)

# Make graph beautiful
fig.update_layout(
    template="plotly_dark",
    title_font_size=28,
    title_x=0.5,
    legend_title_text="",
    hovermode="x unified",
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font=dict(size=14)
)

fig.update_traces(line=dict(width=4))
fig.update_traces(fill='tozeroy')

st.plotly_chart(fig, use_container_width=True)

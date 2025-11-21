import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import linprog
from fpdf import FPDF
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced Energy Distribution", layout="wide")
st.title("Advanced Energy Distribution Agents")
st.markdown("Dynamic 24-hour energy allocation simulation for multiple buildings with PDF report download.")

# ------------------------
# 1. User Inputs
# ------------------------
num_buildings = st.sidebar.number_input("Number of buildings", 5, 50, 10)
total_energy_per_hour = st.sidebar.number_input("Total energy available per hour (kWh)", 500, 10000, 3000)
hours = 24

# ------------------------
# 2. Simulate Building Demand
# ------------------------
np.random.seed(42)
demand = np.random.randint(50, 500, size=(num_buildings, hours))
priority = np.random.randint(1, 5, size=num_buildings)  # 1 = high, 5 = low
buildings = [f"Building {i+1}" for i in range(num_buildings)]

df_demand = pd.DataFrame(demand, columns=[f"Hour {h}" for h in range(1, hours+1)])
df_demand['Building'] = buildings
df_demand['Priority'] = priority
st.subheader("Simulated Building Demand (kWh)")
st.dataframe(df_demand)

# ------------------------
# 3. Optimization Allocation
# ------------------------
allocations = []

for h in range(hours):
    c = -priority  # maximize priority-weighted allocation
    A = [np.ones(num_buildings)]
    b = [total_energy_per_hour]
    bounds = [(0, demand[i, h]) for i in range(num_buildings)]
    res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    allocations.append(res.x)

allocations = np.array(allocations).T  # shape: buildings x hours

# Efficiency calculation
efficiency = allocations / demand * 100

# ------------------------
# 4. Interactive Heatmap
# ------------------------
st.subheader("Efficiency Heatmap (%)")
fig_heatmap = px.imshow(efficiency,
                        labels=dict(x="Hour", y="Building", color="Efficiency (%)"),
                        x=[f"Hour {h}" for h in range(1, hours+1)],
                        y=buildings,
                        color_continuous_scale='Viridis')
st.plotly_chart(fig_heatmap, use_container_width=True)

# ------------------------
# 5. Stacked Bar Chart per Hour
# ------------------------
st.subheader("Hourly Energy Allocation (Stacked)")
fig_bar = go.Figure()
for i, b in enumerate(buildings):
    fig_bar.add_trace(go.Bar(
        x=[f"Hour {h}" for h in range(1, hours+1)],
        y=allocations[i],
        name=b
    ))
fig_bar.update_layout(barmode='stack', title="Energy Allocation per Hour")
st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------
# 6. PDF Report Generation
# ------------------------
st.subheader("Download PDF Report")

def generate_pdf(buildings, demand, allocations, efficiency):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Advanced Energy Distribution Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    
    # Add summary table
    for i, b in enumerate(buildings):
        total_demand = int(demand[i].sum())
        total_alloc = int(allocations[i].sum())
        avg_eff = round(efficiency[i].mean(), 2)
        pdf.cell(0, 8, f"{b}: Total Demand={total_demand} kWh, Allocated={total_alloc} kWh, Avg Efficiency={avg_eff}%", ln=True)
    
    # Add heatmap image
    plt.figure(figsize=(10,5))
    plt.imshow(efficiency, aspect='auto', cmap='viridis', origin='lower')
    plt.colorbar(label='Efficiency (%)')
    plt.xticks(ticks=np.arange(hours), labels=[f"{h}" for h in range(1, hours+1)])
    plt.yticks(ticks=np.arange(len(buildings)), labels=buildings)
    plt.title("Efficiency Heatmap (%)")
    plt.tight_layout()
    heatmap_file = "heatmap.png"
    plt.savefig(heatmap_file)
    plt.close()
    pdf.image(heatmap_file, x=10, y=80, w=190)
    
    file_name = "Advanced_Energy_Report.pdf"
    pdf.output(file_name)
    return file_name

if st.button("Generate PDF Report"):
    pdf_file = generate_pdf(buildings, demand, allocations, efficiency)
    with open(pdf_file, "rb") as f:
        st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")

st.success("Simulation complete! You can explore charts and download the PDF report.")

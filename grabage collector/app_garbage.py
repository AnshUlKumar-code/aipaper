import streamlit as st
import numpy as np
import plotly.graph_objects as go
import heapq

# ----------------------------------------
# GRAPH CREATION
# ----------------------------------------
def create_city_graph(n_nodes, max_weight=10, seed=1):
    np.random.seed(seed)
    graph = {i: {} for i in range(n_nodes)}

    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if np.random.rand() < 0.35:   # ~35% connectivity
                w = np.random.randint(1, max_weight)
                graph[i][j] = w
                graph[j][i] = w
    return graph

# ----------------------------------------
# DIJKSTRA SHORTEST PATHS
# ----------------------------------------
def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    parent = {node: None for node in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: 
            continue
        for v, w in graph[u].items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    return dist, parent

def shortest_path(parent, target):
    path = []
    while target is not None:
        path.append(target)
        target = parent[target]
    return path[::-1]

# ----------------------------------------
# ROUTE COST
# ----------------------------------------
def route_cost(route, graph):
    total = 0
    for i in range(len(route)-1):
        u, v = route[i], route[i+1]
        if v in graph[u]:
            total += graph[u][v]
        else:
            total += 999999  # unreachable
    return total

# ----------------------------------------
# ROUTING BASELINE (ORDERED PICKUP)
# ----------------------------------------
def baseline_routes(depots, bins):
    routes = []
    for d in depots:
        route = [d] + bins + [d]  # simple loop
        routes.append(route)
    return routes

# ----------------------------------------
# OPTIMIZED AGENT ROUTING
# ----------------------------------------
def optimized_routes(graph, depots, bins):
    routes = []
    for depot in depots:
        dist, parent = dijkstra(graph, depot)
        sorted_bins = sorted(bins, key=lambda x: dist[x])  # nearest-first
        route = [depot]
        for b in sorted_bins:
            path = shortest_path(parent, b)
            route.extend(path[1:])  # avoid duplicating nodes
        path_back = shortest_path(parent, depot)
        route.extend(path_back[1:])
        routes.append(route)
    return routes

# ----------------------------------------
# GRAPH PLOT
# ----------------------------------------
def draw_graph(graph, routes_baseline=None, routes_opt=None):

    edges_x = []
    edges_y = []
    pos = {}

    # generate random positions for visualization
    for node in graph:
        pos[node] = (np.random.rand(), np.random.rand())

    for u in graph:
        for v in graph[u]:
            if u < v:
                edges_x += [pos[u][0], pos[v][0], None]
                edges_y += [pos[u][1], pos[v][1], None]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edges_x, y=edges_y,
        mode='lines',
        line=dict(width=1),
        name="Roads"
    ))

    # Nodes
    fig.add_trace(go.Scatter(
        x=[pos[i][0] for i in graph],
        y=[pos[i][1] for i in graph],
        mode='markers+text',
        text=[str(i) for i in graph],
        textposition="top center",
        marker=dict(size=12),
        name="Nodes"
    ))

    return fig

# ----------------------------------------
# STREAMLIT UI
# ----------------------------------------
st.title("🚛 Smart Garbage Collection Routing Optimizer")
st.write("Optimization using Dijkstra + AI agent routing")

n_nodes = st.slider("Number of City Nodes", 6, 25, 12)
n_bins = st.slider("Garbage Bin Count", 2, 10, 4)
n_depots = st.slider("Depot Count", 1, 3, 1)

st.sidebar.header("Random Seed")
seed = st.sidebar.slider("Seed", 1, 999, 10)

graph = create_city_graph(n_nodes, seed=seed)

# pick bins & depots
bins = list(range(1, 1+n_bins))
depots = [0]  # depot always node 0

st.subheader("City Graph")
fig = draw_graph(graph)
st.plotly_chart(fig, use_container_width=True)

# Baseline
base = baseline_routes(depots, bins)

# Optimized
opt = optimized_routes(graph, depots, bins)

# Compute cost
base_cost = sum(route_cost(r, graph) for r in base)
opt_cost = sum(route_cost(r, graph) for r in opt)

st.header("📊 Results Comparison")

col1, col2 = st.columns(2)
col1.metric("Baseline Route Cost", base_cost)
col2.metric("Optimized Cost", opt_cost)

improvement = ((base_cost - opt_cost) / base_cost) * 100 if base_cost > 0 else 0
st.success(f"✨ Optimization Improvement: {improvement:.2f}%")

st.subheader("Baseline Route")
st.write(base)

st.subheader("Optimized Route")
st.write(opt)


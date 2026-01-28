import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
import heapq

st.set_page_config(page_title="Dijkstra Visualizer", layout="wide")

# Modern CSS for the Distance Table
st.markdown("""
    <style>
    .mem-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .node-box {
        background: #26657A;
        color: white;
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        font-family: 'Courier New', Courier, monospace;
    }
    .active-node {
        border: 2px solid #FF4B4B;
        background: #4B1e1e;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Simple Dijkstra Pathfinding")

# 1. Setup Weighted Graph
graph = {
    'A': {'B': 4, 'C': 2},
    'B': {'C': 1, 'D': 5},
    'C': {'D': 8, 'E': 10},
    'D': {'E': 2, 'F': 6},
    'E': {'F': 3},
    'F': {}
}

G = nx.DiGraph()
for u, neighbors in graph.items():
    for v, weight in neighbors.items():
        G.add_edge(u, v, weight=weight)

pos = {'A': (0, 1), 'B': (1, 2), 'C': (1, 0), 'D': (2, 2), 'E': (2, 0), 'F': (3, 1)}

# Sidebar
st.sidebar.header("Configuration")
start_node = st.sidebar.selectbox("Select Start Node", list(graph.keys()))
speed = st.sidebar.slider("Step Delay", 0.5, 3.0, 1.5)

col_graph, col_mem = st.columns([2, 1])

with col_graph:
    plot_spot = st.empty()
    status_spot = st.empty()

with col_mem:
    st.subheader("Shortest Distances")
    dist_spot = st.empty()

def update_ui(distances, current_node):
    html = "<div class='mem-container'>"
    for node, dist in distances.items():
        active_css = "active-node" if node == current_node else ""
        val = "∞" if dist == float('inf') else dist
        html += f"<div class='node-box {active_css}'><span>Node {node}</span> <b>{val}</b></div>"
    html += "</div>"
    dist_spot.markdown(html, unsafe_allow_html=True)

def draw_graph(active_node, visited, discovered_edges):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_facecolor("none")
    
    colors = []
    for n in G.nodes():
        if n == active_node: colors.append("#FF4B4B") # Active
        elif n in visited: colors.append("#26657A")    # Visited
        else: colors.append("#E3B06E")                # Unvisited
            
    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=800, 
            font_color="white", font_weight="bold", ax=ax, edge_color="#333", width=1)
    
    # Highlight only the edges we have explored
    nx.draw_networkx_edges(G, pos, edgelist=discovered_edges, edge_color="#E3B06E", width=2, ax=ax)
    
    # Draw weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
    
    plt.axis("off")
    plot_spot.pyplot(fig)
    plt.close(fig)

def dijkstra(start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]
    visited = set()
    seen_edges = []

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        
        # UI Update: Visiting Node
        status_spot.markdown(f"### 📍 Exploring Node **{current_node}**")
        update_ui(distances, current_node)
        draw_graph(current_node, visited, seen_edges)
        time.sleep(speed)

        for neighbor, weight in graph[current_node].items():
            seen_edges.append((current_node, neighbor))
            distance = current_distance + weight
            
            # Draw discovery transition
            draw_graph(current_node, visited, seen_edges)
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))
                status_spot.write(f"✨ Updated Node {neighbor} distance to {distance}")
                update_ui(distances, current_node)
            
            time.sleep(speed * 0.5)

        visited.add(current_node)

    status_spot.success("🎉 Dijkstra Search Complete!")
    update_ui(distances, None)

if st.sidebar.button("▶️ Start Dijkstra"):
    dijkstra(start_node)

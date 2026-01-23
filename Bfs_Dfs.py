import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
from collections import deque

st.set_page_config(page_title="Graph Traversal Pro", layout="wide")
st.title("🎓 Graph Traversal & Loop Analysis")

# 1. Graph Configuration
graph_data = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['B'],
    'F': []
}

G = nx.DiGraph(graph_data)
# Static positions for a clean "Tree-like" look
pos = {'A': (0, 2), 'B': (-1, 1), 'C': (1, 1), 'D': (-1.5, 0), 'E': (-0.5, 0), 'F': (1, 0)}

# Sidebar Controls
st.sidebar.header("Algorithm Settings")
algo_choice = st.sidebar.radio("Select Traversal:", ["BFS (Breadth-First)", "DFS (Depth-First)"])
speed = st.sidebar.slider("Animation Speed", 0.5, 2.0, 1.0)

# Main UI Layout
col_graph, col_info = st.columns([2, 1])

with col_graph:
    st.subheader("Live Visualization")
    plot_spot = st.empty()
    # This will show the order dynamically
    order_spot = st.empty()

with col_info:
    st.subheader("Traversal Log")
    log_area = st.container()

def run_visualizer(mode):
    visited = set()
    container = ['A'] # Starting Node
    order = []
    loops = []
    
    node_colors = {n: 'skyblue' for n in G.nodes()}
    edge_colors = {(u, v): 'gray' for u, v in G.edges()}

    while container:
        # ALGORITHM LOGIC: Queue vs Stack
        if mode == "BFS (Breadth-First)":
            current = container.pop(0) # FIFO
        else:
            current = container.pop()    # LIFO
        
        if current not in visited:
            visited.add(current)
            order.append(current)
            node_colors[current] = 'orange'
            
            # --- UPDATE LIVE ORDER TEXT ---
            order_spot.markdown(f"### 📍 Visiting Order: {' → '.join(order)}")
            
            # --- DRAW GRAPH ---
            fig, ax = plt.subplots(figsize=(7, 5))
            nx.draw(G, pos, with_labels=True, 
                    node_color=[node_colors[n] for n in G.nodes()],
                    edge_color=[edge_colors[e] for e in G.edges()],
                    node_size=500, connectionstyle='arc3, rad = 0.3', 
                    arrows=True, arrowsize=20, ax=ax, font_weight='bold')
            plot_spot.pyplot(fig)
            plt.close(fig)
            
            with log_area:
                st.write(f"✅ Visited Node **{current}**")
            
            time.sleep(speed)

            # --- PROCESS NEIGHBORS ---
            neighbors = graph_data[current]
            if mode == "DFS (Depth-First)":
                neighbors = reversed(neighbors)

            for neighbor in neighbors:
                if neighbor in visited:
                    # Highlight Loop but keep going
                    loops.append((current, neighbor))
                    edge_colors[(current, neighbor)] = 'red'
                    node_colors[neighbor] = 'red'
                else:
                    container.append(neighbor)
                    if node_colors[neighbor] == 'skyblue':
                        node_colors[neighbor] = 'lightgreen' # Discovered

    return order, loops

if st.sidebar.button("▶️ Start Traversal"):
    final_order, found_loops = run_visualizer(algo_choice)
    
    st.divider()
    st.success(f"🎊 Execution Finished! Final Sequence: {' → '.join(final_order)}")
    
    if found_loops:
        st.warning(f"⚠️ Loop(s) detected at: {', '.join([f'{u}→{v}' for u, v in found_loops])}")
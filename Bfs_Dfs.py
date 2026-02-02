import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time

st.set_page_config(page_title = "Graph Traversal Pro", layout = "wide")

# Modern CSS
st.markdown(
    """
    <style>
    .mem-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 300px;
    }
    .node-box {
        background: linear-gradient(135deg, #4A90E2, #50E3C2);
        color: white;
        padding: 12px;
        margin: 10px 0;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌳 Modern Graph Discovery: DFS vs BFS")

# Graph Configuration
graph_data = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["B"],
    "F": [],
}
G = nx.DiGraph(graph_data)
pos = {
    "A": (0, 2),
    "B": (-1.5, 1),
    "C": (1.5, 1),
    "D": (-2, 0),
    "E": (-1, 0),
    "F": (1.5, 0),
}

# Sidebar
st.sidebar.header("Pacing Controls")
algo_choice = st.sidebar.radio(
    "Algorithm:", ["BFS (Breadth-First)", "DFS (Depth-First)"]
)
speed = st.sidebar.slider("Step Duration (seconds)", 1.0, 2.0)

col_graph, col_mem = st.columns([2, 1])

with col_graph:
    plot_spot = st.empty()
    path_spot = st.empty()

with col_mem:
    st.subheader("Memory Buffer")
    mem_spot = st.empty()


def draw_graph_step(visible_nodes, visible_edges, active_node = None, visited_list = None):
    visited_list = visited_list or []
    fig, ax = plt.subplots(figsize=(6, 4), facecolor = "none")
    ax.set_facecolor("none")
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-0.5, 2.5)
    plt.axis("off")

    node_colors = []
    for n in visible_nodes:
        if n == active_node:
            node_colors.append("#FF4B4B")  # RED: Active
        elif n in visited_list:
            node_colors.append("#26657A")  # BLUE: Visited
        else:
            node_colors.append("#E3B06E")  # GOLD: Unvisited/Discovered

    nx.draw(
        G,
        pos,
        nodelist = list(visible_nodes),
        edgelist = visible_edges,
        with_labels = True,
        node_color = node_colors,
        edge_color = "#262424",
        node_size = 1200,
        font_weight = "bold",
        font_color = "white",
        arrows = True,
        arrowsize = 20,
        ax = ax,
        connectionstyle = "arc3,rad=0.25",
        width = 2,
    )

    plot_spot.pyplot(fig)
    plt.close(fig)


def update_mem_ui(container, mode):
    label = (
        "BOTTOM (Queue - FIFO)"
        if mode == "BFS (Breadth-First)"
        else "TOP (Stack - LIFO)"
    )
    # We display the stack so the last item added is at the top
    items = list(container)
    if mode == "DFS (Depth-First)":
        items = items[::-1]

    html = f"<div class='mem-container'><b>{label}</b>"
    for item in items:
        html += f"<div class='node-box'>{item}</div>"
    html += "</div>"
    mem_spot.markdown(html, unsafe_allow_html=True)


def run_animation(mode):
    # PHASE 1: PREVIEW
    path_spot.info("Analyzing Structure...")
    draw_graph_step(G.nodes(), G.edges(), visited_list = [])
    time.sleep(2)

    # PHASE 2: RESET AND GROW
    path_spot.empty()
    visited = []
    frontier = ["A"]  # This is our Stack or Queue
    shown_nodes = {"A"}
    shown_edges = []

    while frontier:
        update_mem_ui(frontier, mode)

        # POP logic:
        # BFS: Pop from front (index 0)
        # DFS: Pop from back (last item)
        current = frontier.pop(0) if mode == "BFS (Breadth-First)" else frontier.pop()

        if current not in visited:
            # 1. VISITING: Highlight Active Node
            draw_graph_step(
                shown_nodes, shown_edges, active_node=current, visited_list=visited
            )
            path_spot.markdown(f"### 📍 Processing Node: **{current}**")
            time.sleep(speed)

            visited.append(current)
            path_spot.markdown(f"### 📍 Path: {' → '.join(visited)}")

            # 2. DISCOVERY: Find neighbors
            neighbors = graph_data[current]

            # To maintain expected order in DFS (A -> B before A -> C),
            # we don't necessarily need to reverse here because the stack handles it,
            # but for visualization consistency:
            for n in neighbors:
                shown_nodes.add(n)
                shown_edges.append((current, n))

                # Show neighbor discovery
                draw_graph_step(
                    shown_nodes, shown_edges, active_node=current, visited_list=visited
                )

                if n not in visited:
                    # In standard DFS, we add it even if it's in frontier to ensure
                    # it moves to the "Top" of the stack
                    if mode == "DFS (Depth-First)" and n in frontier:
                        frontier.remove(n)
                    frontier.append(n)
                    update_mem_ui(frontier, mode)

                time.sleep(speed * 0.5)

    path_spot.success(f"Execution Complete! Final Path: {' → '.join(visited)}")


if st.sidebar.button("▶️ Start Slow-Motion Traversal"):
    run_animation(algo_choice)

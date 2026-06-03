import itertools
import matplotlib.pyplot as plt
import networkx as nx

def make_graph(n):
    G = nx.Graph()
    elemen = list(range(1, n + 1))
    vertices = [tuple(p) for p in itertools.permutations(elemen)]
    G.add_nodes_from(vertices)

    for v in G.nodes:
        for i in range(1, n - 1):
            list_v = list(v)
            list_v[i], list_v[i + 1] = list_v[i + 1], list_v[i]
            neighbor = tuple(list_v)
            G.add_edge(v, neighbor)

        for i in range(1, n):
            list_v = list(v)
            list_v[0], list_v[i] = list_v[i], list_v[0]
            neighbor = tuple(list_v)
            G.add_edge(v, neighbor)
    return G

def edge_subversion(G, edges_target):
    G_residual = G.copy()
    affected_nodes = set()

    for u, v in edges_target:
        affected_nodes.add(u)
        affected_nodes.add(v)

    affected_edges = set()
    for u, v in G.edges:
        edge = (u, v) if u < v else (v, u)
        if u in affected_nodes or v in affected_nodes:
            edges_target_sorted = [(e1, e2) if e1 < e2 else (e2, e1) for e1, e2 in edges_target]
            if edge not in edges_target_sorted:
                affected_edges.add(edge)
    G_residual.remove_nodes_from(affected_nodes)


    return G_residual, affected_nodes, affected_edges

n = 4
G = make_graph(n)

isolated_node = tuple(range(1, n + 1))

target_neighbors = list(G.neighbors(isolated_node))

edges_target = []

for tetangga in target_neighbors:
    external_edge = [e for e in G.edges(tetangga) if isolated_node not in e]
    edges_target.append(external_edge[0])

edges_target = edges_target[:2 * n - 3]

G_residual, affected_nodes, affected_edges = edge_subversion(G, edges_target)

pos = nx.kamada_kawai_layout(G)
labels = {node: "".join(map(str, node)) for node in G.nodes}

# plotting
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# Normal graph
ax1.set_title(f"1. Normal BSn Graph")
nx.draw_networkx_edges(G, pos, ax=ax1, edge_color="gray", width=1)
nx.draw_networkx_nodes(G, pos, ax=ax1, node_color="lightblue", node_size=400)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, ax=ax1)

# Targeted graph
ax2.set_title(f"2. Targeted Graph")
node_colors = []
for node in G.nodes:
    if node == isolated_node:
        node_colors.append("yellow") 
    elif node in affected_nodes:
        node_colors.append("orange")
    else:
        node_colors.append("lightgreen")

nx.draw_networkx_nodes(G, pos, ax=ax2, node_color=node_colors, node_size=400)
nx.draw_networkx_labels(ax2, pos, labels=labels, font_size=7, ax=ax2)

edges_target_sorted = [(u, v) if u < v else (v, u) for u, v in edges_target]
for u, v in G.edges:
    edge = (u, v) if u < v else (v, u)
    if edge in edges_target_sorted:
        nx.draw_networkx_edges(G, pos, edgelist=[edge], ax=ax2, edge_color="red", width=2.5)
    elif edge in affected_edges:
        nx.draw_networkx_edges(G, pos, edgelist=[edge], ax=ax2, edge_color="orange", width=1, style="dashed")
    else:
        nx.draw_networkx_edges(G, pos, edgelist=[edge], ax=ax2, edge_color="green", width=1)

# Final graph
ax3.set_title(f"3. Final Graph")
labels_sisa = {node: labels[node] for node in G_residual.nodes}
node_colors = ["yellow" if node == isolated_node else "lightgreen" for node in G_residual.nodes]

nx.draw_networkx_nodes(G_residual, pos, ax=ax3, node_color=node_colors, node_size=400)
nx.draw_networkx_edges(G_residual, pos, ax=ax3, edge_color="green", width=1.5)
nx.draw_networkx_labels(G_residual, pos, labels=labels_sisa, font_size=7, ax=ax3)

plt.tight_layout()
plt.show()
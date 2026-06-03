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


def vertex_subversion(G, set_faulty_nodes):
    G_residual = G.copy()
    targeted_node = set()

    for node in set_faulty_nodes:
        if node in G_residual:
            targeted_node.add(node)
            for neighbor in G.neighbors(node):
                targeted_node.add(neighbor)

    G_residual.remove_nodes_from(targeted_node)
    return G_residual, targeted_node


def swap_position(node, i, j):
    idx_i, idx_j = i - 1, j - 1
    list_node = list(node)
    list_node[idx_i], list_node[idx_j] = list_node[idx_j], list_node[idx_i]
    return tuple(list_node)


def find_node(n, x):
    A = []
    B = []

    # Set A
    for i in range(2, n):
        if i % 2 == 0:
            node_A = swap_position(x, 1, i)
            node_A = swap_position(node_A, 1, i + 1)
            A.append(node_A)

    # Set B
    if n % 2 == 0:
        for i in range(3, n - 2, 4):
            node_b = swap_position(x, i, i + 1)
            node_b = swap_position(node_b, i + 2, i + 3)
            B.append(node_b)
        left_node = swap_position(x, 1, n)
        left_node = swap_position(left_node, n - 1, n)
        B.append(left_node)
    else:
        for i in range(3, n - 2, 4):
            node_b = swap_position(x, i, i + 1)
            node_b = swap_position(node_b, i + 2, i + 3)
            B.append(node_b)
        
        if n % 4 == 1:
            left_node = swap_position(x, n - 2, n - 1)
            left_node = swap_position(left_node, n - 1, n)
            B.append(left_node)

    return A + B

n = 4
G = make_graph(n)

isolated_node = tuple(range(1, n + 1))
targeted_nodes = find_node(n, isolated_node)

G_residual, targeted_node = vertex_subversion(G, targeted_nodes)

pos = nx.kamada_kawai_layout(G)
labels = {node: "".join(map(str, node)) for node in G.nodes}

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# 1. Normal Graph
ax1.set_title(f"1. Normal BSn graph")
nx.draw_networkx_edges(G, pos, ax=ax1, edge_color="gray", width=1)
nx.draw_networkx_nodes(G, pos, ax=ax1, node_color="lightblue", node_size=400)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, ax=ax1)

# 2. Targeted Graph
ax2.set_title(f"2. Targeted Graph")
node_colors_ax2 = []
for node in G.nodes:
    if node == isolated_node:
        node_colors_ax2.append("yellow")
    elif node in targeted_nodes:
        node_colors_ax2.append("red")
    elif node in targeted_node:
        node_colors_ax2.append("orange")
    else:
        node_colors_ax2.append("lightgreen")

nx.draw_networkx_nodes(G, pos, ax=ax2, node_color=node_colors_ax2, node_size=400)
nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, ax=ax2)

for u, v in G.edges:
    if u in targeted_node or v in targeted_node:
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax2, edge_color="orange", width=1, style="dashed")
    else:
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax2, edge_color="green", width=1)

# 3. Final Graph
ax3.set_title(f"3. Final Graph")
labels_sisa = {node: labels[node] for node in G_residual.nodes}
node_colors_sisa = ["yellow" if node == isolated_node else "lightgreen" for node in G_residual.nodes]

nx.draw_networkx_edges(G_residual, pos, ax=ax3, edge_color="green", width=1.5)
nx.draw_networkx_nodes(G_residual, pos, ax=ax3, node_color=node_colors_sisa, node_size=400)
nx.draw_networkx_labels(G_residual, pos, labels=labels_sisa, font_size=7, ax=ax3)

plt.tight_layout()
plt.show()

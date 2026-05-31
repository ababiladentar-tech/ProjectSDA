import itertools
import matplotlib.pyplot as plt
import networkx as nx

def buat_bubble_sort_star_graph(n):
    G = nx.Graph()
    elemen = list(range(1, n + 1))
    vertices = [tuple(p) for p in itertools.permutations(elemen)]
    G.add_nodes_from(vertices)

    for v in G.nodes:
        for i in range(1, n - 1):
            list_v = list(v)
            list_v[i], list_v[i + 1] = list_v[i + 1], list_v[i]
            G.add_edge(v, tuple(list_v))
        for i in range(1, n):
            list_v = list(v)
            list_v[0], list_v[i] = list_v[i], list_v[0]
            G.add_edge(v, tuple(list_v))
    return G

def simulasi_edge_subversion_murni(G, edges_target):
    nodes_terserang = set()
    for u, v in edges_target:
        nodes_terserang.add(u)
        nodes_terserang.add(v)

    edges_kedampak = set()
    for u, v in G.edges:
        edge_aktif = (u, v) if u < v else (v, u)
        if u in nodes_terserang or v in nodes_terserang:
            edges_target_sorted = [
                (e1, e2) if e1 < e2 else (e2, e1) for e1, e2 in edges_target
            ]
            if edge_aktif not in edges_target_sorted:
                edges_kedampak.add(edge_aktif)

    # G ⊖ F = G - V(F)
    G_residual = G.copy()
    G_residual.remove_nodes_from(nodes_terserang)

    return G_residual, nodes_terserang, edges_kedampak

n = 4
G_awal = buat_bubble_sort_star_graph(n)

node_target = tuple(range(1, n + 1))

tetangga_target = list(G_awal.neighbors(node_target))

edges_yang_diserang = []
for tetangga in tetangga_target:
    jalur_keluar = [e for e in G_awal.edges(tetangga) if node_target not in e]
    edges_yang_diserang.append(jalur_keluar[0])

# Validasi jumlah edge yang diserang tidak melebihi 2n-3
edges_yang_diserang = edges_yang_diserang[:2 * n - 3]

# Jalankan Eksekusi
G_sisa, nodes_mati, edges_rontok = simulasi_edge_subversion_murni(
    G_awal, edges_yang_diserang
)

pos = nx.kamada_kawai_layout(G_awal)
labels_awal = {node: "".join(map(str, node)) for node in G_awal.nodes}

# Membuat canvas 
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# --- PLOT 1: Normal ---
ax1.set_title(f"1. Graf Normal BS_{n}")
nx.draw_networkx_edges(G_awal, pos, ax=ax1, edge_color="gray", width=1)
nx.draw_networkx_nodes(G_awal, pos, ax=ax1, node_color="lightblue", node_size=400)
nx.draw_networkx_labels(G_awal, pos, labels=labels_awal, font_size=7, ax=ax1)

# --- PLOT 2: Graf Serangan ---
ax2.set_title(f"2. Graf Serangan ({len(edges_yang_diserang)} Edge)")
node_colors = []
for node in G_awal.nodes:
    if node == node_target:
        node_colors.append("yellow") 
    elif node in nodes_mati:
        node_colors.append("orange")
    else:
        node_colors.append("lightgreen")

nx.draw_networkx_nodes(G_awal, pos, ax=ax2, node_color=node_colors, node_size=400)
nx.draw_networkx_labels(ax2, pos, labels=labels_awal, font_size=7, ax=ax2)

edges_diserang_sorted = [(u, v) if u < v else (v, u) for u, v in edges_yang_diserang]
for u, v in G_awal.edges:
    edge_skrg = (u, v) if u < v else (v, u)
    if edge_skrg in edges_diserang_sorted:
        nx.draw_networkx_edges(G_awal, pos, edgelist=[edge_skrg], ax=ax2, edge_color="red", width=2.5)
    elif edge_skrg in edges_rontok:
        nx.draw_networkx_edges(G_awal, pos, edgelist=[edge_skrg], ax=ax2, edge_color="orange", width=1, style="dashed")
    else:
        nx.draw_networkx_edges(G_awal, pos, edgelist=[edge_skrg], ax=ax2, edge_color="green", width=1)

# --- PLOT 3: Graf Sisa ---
ax3.set_title("3. Graf Sisa ")
labels_sisa = {node: labels_awal[node] for node in G_sisa.nodes}
node_colors_sisa = ["yellow" if node == node_target else "lightgreen" for node in G_sisa.nodes]

nx.draw_networkx_nodes(G_sisa, pos, ax=ax3, node_color=node_colors_sisa, node_size=400)
nx.draw_networkx_edges(G_sisa, pos, ax=ax3, edge_color="green", width=1.5)
nx.draw_networkx_labels(G_sisa, pos, labels=labels_sisa, font_size=7, ax=ax3)

apakah_terhubung = nx.is_connected(G_sisa)
print(f"Total Edge Penyerang Aktif: {len(edges_yang_diserang)}")
print(f"Apakah Graf Sisa Masih Nyambung? {apakah_terhubung}")

plt.tight_layout()
plt.show()
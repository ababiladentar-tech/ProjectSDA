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
            tetangga = tuple(list_v)
            G.add_edge(v, tetangga)

        for i in range(1, n):
            list_v = list(v)
            list_v[0], list_v[i] = list_v[i], list_v[0]
            tetangga = tuple(list_v)
            G.add_edge(v, tetangga)

    return G


def subversi_vertex(G, set_faulty_nodes):
    G_residual = G.copy()
    nodes_yang_dihapus = set()

    for node in set_faulty_nodes:
        if node in G_residual:
            nodes_yang_dihapus.add(node)
            for tetangga in G.neighbors(node):
                nodes_yang_dihapus.add(tetangga)

    G_residual.remove_nodes_from(nodes_yang_dihapus)
    return G_residual, nodes_yang_dihapus


def swap_posisi(node, i, j):
    idx_i, idx_j = i - 1, j - 1
    list_node = list(node)
    list_node[idx_i], list_node[idx_j] = list_node[idx_j], list_node[idx_i]
    return tuple(list_node)


def cari_node_penyerang_otomatis(n, x):
    """Mencari node penyerang dengan logika perulangan Set B yang disempurnakan."""
    A = []
    B = []

    # 1. Set A: Selalu konsisten menutup jalur pola awal
    for i in range(2, n):
        if i % 2 == 0:
            node_A = swap_posisi(x, 1, i)
            node_A = swap_posisi(node_A, 1, i + 1)
            A.append(node_A)

    # 2. Set B: Menyapu bersih sisa jalur yang belum ditutup
    if n % 2 == 0:
        # Penanganan khusus dimensi GENAP (misal 4, 6, 8)
        for i in range(3, n - 2, 4):
            node_b = swap_posisi(x, i, i + 1)
            node_b = swap_posisi(node_b, i + 2, i + 3)
            B.append(node_b)
        
        # Wajib ada ekor buat nutup jalur akhir di dimensi genap
        node_ekor = swap_posisi(x, 1, n)
        node_ekor = swap_posisi(node_ekor, n - 1, n)
        B.append(node_ekor)
    else:
        # Penanganan khusus dimensi GANJIL (misal 5, 7, 9)
        for i in range(3, n - 2, 4):
            node_b = swap_posisi(x, i, i + 1)
            node_b = swap_posisi(node_b, i + 2, i + 3)
            B.append(node_b)
        
        # Ekor hanya ditambahkan jika ada sisa satu jalur yang belum berpasangan
        if n % 4 == 1:
            node_ekor = swap_posisi(x, n - 2, n - 1)
            node_ekor = swap_posisi(node_ekor, n - 1, n)
            B.append(node_ekor)

    return A + B

n = 4
G_awal = buat_bubble_sort_star_graph(n)

node_target_x = tuple(range(1, n + 1))
node_pembunuh = cari_node_penyerang_otomatis(n, node_target_x)

G_setelah_serangan, target_terhapus = subversi_vertex(G_awal, node_pembunuh)

pos = nx.kamada_kawai_layout(G_awal)
labels_awal = {node: "".join(map(str, node)) for node in G_awal.nodes}

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(24, 7))

# 1. Gambar Graf Normal
ax1.set_title(f"1. Graf Normal BSn")
nx.draw_networkx_edges(G_awal, pos, ax=ax1, edge_color="gray", width=1)
nx.draw_networkx_nodes(G_awal, pos, ax=ax1, node_color="lightblue", node_size=400)
# Label dimatiin biar nggak nutupin warna node kalo grafnya makin padet
nx.draw_networkx_labels(G_awal, pos, labels=labels_awal, font_size=7, ax=ax1)

# 2. Gambar Graf Serangan
ax2.set_title("2. Graf Serangan")
node_colors_ax2 = []
for node in G_awal.nodes:
    if node == node_target_x:
        node_colors_ax2.append("yellow")
    elif node in node_pembunuh:
        node_colors_ax2.append("red")
    elif node in target_terhapus:
        node_colors_ax2.append("orange")
    else:
        node_colors_ax2.append("lightgreen")

nx.draw_networkx_nodes(G_awal, pos, ax=ax2, node_color=node_colors_ax2, node_size=400)
nx.draw_networkx_labels(G_awal, pos, labels=labels_awal, font_size=7, ax=ax2)

for u, v in G_awal.edges:
    if u in target_terhapus or v in target_terhapus:
        nx.draw_networkx_edges(G_awal, pos, edgelist=[(u, v)], ax=ax2, edge_color="orange", width=1, style="dashed")
    else:
        nx.draw_networkx_edges(G_awal, pos, edgelist=[(u, v)], ax=ax2, edge_color="green", width=1)

# 3. Gambar Graf Sisa
ax3.set_title("3. Graf Sisa")
labels_sisa = {node: labels_awal[node] for node in G_setelah_serangan.nodes}
node_colors_sisa = ["yellow" if node == node_target_x else "lightgreen" for node in G_setelah_serangan.nodes]

nx.draw_networkx_edges(G_setelah_serangan, pos, ax=ax3, edge_color="green", width=1.5)
nx.draw_networkx_nodes(G_setelah_serangan, pos, ax=ax3, node_color=node_colors_sisa, node_size=400)
nx.draw_networkx_labels(G_setelah_serangan, pos, labels=labels_sisa, font_size=7, ax=ax3)

# Eksekusi output terminal
apakah_terhubung = nx.is_connected(G_setelah_serangan)
print(f"Total node penyerang aktif: {len(node_pembunuh)}")
print(f"Apakah Graf Sisa Masih Nyambung? {apakah_terhubung}")
if node_target_x in G_setelah_serangan:
    print(f"Derajat node target setelah serangan: {G_setelah_serangan.degree(node_target_x)}")

plt.tight_layout()
plt.show()
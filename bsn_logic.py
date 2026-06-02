from __future__ import annotations

import argparse
import itertools
import json
from math import factorial
from typing import Dict, Iterable, List, Sequence, Set, Tuple

# Tipe data untuk vertex (node) dalam graf - merupakan tuple dari integer
Vertex = Tuple[int, ...]


# Penjelasan: Menukar dua elemen pada posisi tertentu dalam vertex
def apply_transposition(vertex: Sequence[int], left: int, right: int) -> Vertex:
    """Melakukan transposisi (pertukaran) dua elemen pada posisi left dan right"""
    swapped = list(vertex)
    swapped[left], swapped[right] = swapped[right], swapped[left]
    return tuple(swapped)


# Penjelasan: Menghasilkan semua vertex (permutasi) untuk graf BSn
def generate_vertices(n: int) -> List[Vertex]:
    """Menghasilkan semua permutasi dari 1 hingga n sebagai vertex dalam graf"""
    return list(itertools.permutations(range(1, n + 1)))


# Penjelasan: Membangun graf Bubble-Sort Star (BSn) dengan menghubungkan vertex melalui edge
def build_bsn(n: int) -> Dict[str, object]:
    """Membangun graf Bubble-Sort Star dengan n dimensi.
    
    Graf ini memiliki dua tipe edge:
    - Bubble: transposisi elemen bersebelahan (i, i+1) untuk i=1 hingga n-2
    - Star: transposisi elemen pertama dengan elemen lain (0, i) untuk i=1 hingga n-1
    """
    vertices = generate_vertices(n)
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    adjacency: List[Set[int]] = [set() for _ in vertices]
    edge_set: Set[Tuple[int, int, str]] = set()

    for index, vertex in enumerate(vertices):
        for i in range(1, n - 1):
            neighbor = apply_transposition(vertex, i, i + 1)
            neighbor_index = vertex_index[neighbor]
            left, right = sorted((index, neighbor_index))
            if (left, right, "bubble") not in edge_set:
                adjacency[left].add(right)
                adjacency[right].add(left)
                edge_set.add((left, right, "bubble"))

        for i in range(1, n):
            neighbor = apply_transposition(vertex, 0, i)
            neighbor_index = vertex_index[neighbor]
            left, right = sorted((index, neighbor_index))
            if (left, right, "star") not in edge_set:
                adjacency[left].add(right)
                adjacency[right].add(left)
                edge_set.add((left, right, "star"))

    return {
        "n": n,
        "vertices": vertices,
        "vertex_index": vertex_index,
        "adjacency": adjacency,
        "edge_count": len(edge_set),
        "vertex_count": len(vertices),
        "degree": (2 * n) - 3,
        "theoretical_kappa_nb": (3 * n - 2) // 4,
        "theoretical_lambda_nb": (2 * n) - 3,
    }
# Penjelasan: Menghitung cut set berdasarkan teorema untuk graf BSn
def theorem_cut_set(graph: Dict[str, object]) -> List[int]:
    """Menghitung himpunan vertex yang memotong graf berdasarkan teorema.
    
    Fungsi ini menggunakan operasi transposisi spesifik untuk menghasilkan
    vertex-vertex yang akan membentuk cut set minimal.
    """
    n = int(graph["n"])
    if n < 4:
        return []

    base = tuple(range(1, n + 1))
    vertex_index: Dict[Vertex, int] = graph["vertex_index"]  # type: ignore[assignment]

    cut_set: List[int] = []
    seen: Set[Vertex] = set()

    def add_vertex(operations: Iterable[Tuple[int, int]]) -> None:
        vertex = base
        for left, right in operations:
            vertex = apply_transposition(vertex, left - 1, right - 1)
        if vertex in seen:
            return
        seen.add(vertex)
        cut_set.append(vertex_index[vertex])

    for i in range(2, n, 2):
        add_vertex(((1, i), (1, i + 1)))

    residue = n % 4
    if residue == 0:
        pair_end = n - 5
    elif residue == 1:
        pair_end = n - 6
    elif residue == 2:
        pair_end = n - 3
    else:
        pair_end = n - 4

    for start in range(3, pair_end + 1, 4):
        add_vertex(((start, start + 1), (start + 2, start + 3)))

    if residue in (0, 2):
        add_vertex(((1, n), (n - 1, n)))
    elif residue == 1:
        add_vertex(((n - 2, n - 1), (n - 1, n)))

    return cut_set


# Penjelasan: Menghitung closed neighborhood - vertex yang dihapus termasuk tetangga mereka
def closed_neighborhood(adjacency: Sequence[Set[int]], seed_set: Iterable[int]) -> Set[int]:
    """Menghitung closed neighborhood dari seed_set.
    
    Closed neighborhood mencakup vertex dalam seed_set dan semua tetangganya.
    """
    removed = set(seed_set)
    for index in seed_set:
        removed.update(adjacency[index])
    return removed


# Penjelasan: Menganalisis struktur graf yang tersisa setelah penghapusan vertex
def analyze_remaining_graph(adjacency: Sequence[Set[int]], remaining: List[int]) -> str:
    """Menganalisis sifat graf yang tersisa setelah vertex dihapus.
    
    Return values:
    - 'empty': tidak ada vertex yang tersisa
    - 'complete': semua vertex yang tersisa terhubung penuh (complete graph)
    - 'disconnected': graf terbagi menjadi beberapa komponen
    - 'connected': graf terhubung tapi tidak complete
    """
    if not remaining:
        return "empty"

    remaining_set = set(remaining)
    is_complete = True

    for index in remaining:
        degree = sum(1 for neighbor in adjacency[index] if neighbor in remaining_set)
        if degree != len(remaining) - 1:
            is_complete = False
            break

    if is_complete:
        return "complete"

    components = 0
    visited: Set[int] = set()

    for start in remaining:
        if start in visited:
            continue
        components += 1
        stack = [start]
        visited.add(start)

        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining_set and neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

    return "disconnected" if components > 1 else "connected"


# Penjelasan: Menghitung nilai eksak kappa (vertex connectivity) untuk graf BSn
def exact_kappa_nb(graph: Dict[str, object], max_n: int = 5) -> Dict[str, object] | None:
    """Menghitung vertex connectivity (kappa) secara eksak dengan brute force.
    
    Kappa adalah jumlah minimum vertex yang harus dihapus untuk membuat graf
    tidak terhubung atau kosong. Fungsi ini mencoba semua kombinasi hingga
    ditemukan cut set yang valid.
    """
    n = int(graph["n"])
    if n > max_n:
        return None

    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    vertices = list(range(int(graph["vertex_count"])))
    target = int(graph["theoretical_kappa_nb"])

    for k in range(1, target + 1):
        for subset in itertools.combinations(vertices, k):
            removed = closed_neighborhood(adjacency, subset)
            remaining = [index for index in vertices if index not in removed]
            reason = analyze_remaining_graph(adjacency, remaining)
            if reason in {"empty", "complete", "disconnected"}:
                return {
                    "k": k,
                    "cut_set": list(subset),
                    "removed": sorted(removed),
                    "remaining": remaining,
                    "reason": reason,
                }
    return None


# Penjelasan: Menghitung edge connectivity (lambda) secara eksak dengan brute force
def exact_lambda_nb(graph: Dict[str, object], max_n: int = 5) -> Dict[str, object] | None:
    """Menghitung edge connectivity (lambda) secara eksak.

    Fungsi ini mencoba semua kombinasi edge hingga menemukan satu set
    edge dengan ukuran k yang membuat graf terputus (disconnected).
    Hanya cocok untuk graf kecil (n <= max_n) karena kompleksitas kombinatorial.
    """
    n = int(graph["n"])
    if n > max_n:
        return None

    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    vertex_count = int(graph["vertex_count"])
    vertices = list(range(vertex_count))
    target = int(graph["theoretical_lambda_nb"])

    # Kumpulkan semua edge unik sebagai pasangan (u, v)
    edges: List[Tuple[int, int]] = []
    seen_edges: Set[Tuple[int, int]] = set()
    for u in range(vertex_count):
        for v in adjacency[u]:
            a, b = sorted((u, v))
            if (a, b) not in seen_edges:
                seen_edges.add((a, b))
                edges.append((a, b))

    # Coba semua kombinasi edge dari ukuran 1..target
    for k in range(1, target + 1):
        for subset in itertools.combinations(edges, k):
            # Buat salinan adjacency dan hapus edge-edge dalam subset
            new_adj: List[Set[int]] = [set(neigh) for neigh in adjacency]
            for (a, b) in subset:
                new_adj[a].discard(b)
                new_adj[b].discard(a)

            # Analisis konektivitas pada graf hasil penghapusan edge
            reason = analyze_remaining_graph(new_adj, vertices)
            if reason == "disconnected":
                return {
                    "k": k,
                    "cut_edges": list(subset),
                    "reason": reason,
                }

    return None


# Penjelasan: Subversi vertex dengan menghapus node dan closed neighborhood mereka
def subversi_vertex(graph: Dict[str, object], faulty_nodes: List[int]) -> Tuple[Dict[str, object], Set[int]]:
    """Menghapus faulty_nodes dan semua tetangga mereka (closed neighborhood).
    
    Return: (modified adjacency, removed nodes)
    """
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    nodes_yang_dihapus = set()
    
    for node in faulty_nodes:
        nodes_yang_dihapus.add(node)
        nodes_yang_dihapus.update(adjacency[node])
    
    return nodes_yang_dihapus


# Penjelasan: Mencari node penyerang otomatis berdasarkan pola
def cari_node_penyerang_otomatis(n: int, graph: Dict[str, object], target_index: int | None = None) -> List[int]:
    """Mencari node penyerang dengan logika perulangan Set B yang disempurnakan.
    
    Jika target_index diberikan, hitung berdasarkan permutasi node target.
    """
    if target_index is None:
        base = tuple(range(1, n + 1))
    else:
        base = graph["vertices"][target_index]

    vertex_index: Dict[Vertex, int] = graph["vertex_index"]  # type: ignore[assignment]
    
    A = []
    B = []
    
    # Set A: Selalu konsisten menutup jalur pola awal
    for i in range(2, n):
        if i % 2 == 0:
            node_a = apply_transposition(base, 0, i - 1)
            node_a = apply_transposition(node_a, 0, i)
            if node_a in vertex_index:
                A.append(vertex_index[node_a])
    
    # Set B: Menyapu bersih sisa jalur
    for i in range(3, n - 2, 4):
        node_b = apply_transposition(base, i - 1, i)
        node_b = apply_transposition(node_b, i + 1, i + 2)
        if node_b in vertex_index:
            B.append(vertex_index[node_b])

    if n % 2 == 0:
        node_ekor = apply_transposition(base, 0, n - 1)
        node_ekor = apply_transposition(node_ekor, n - 2, n - 1)
        if node_ekor in vertex_index:
            B.append(vertex_index[node_ekor])
    elif n % 4 == 1:
        node_ekor = apply_transposition(base, n - 3, n - 2)
        node_ekor = apply_transposition(node_ekor, n - 2, n - 1)
        if node_ekor in vertex_index:
            B.append(vertex_index[node_ekor])

    return A + B


def vertex_attack_fault_set(graph: Dict[str, object], target_index: int) -> List[int]:
    """Menghasilkan himpunan F node yang diserang berdasarkan target."""
    n = int(graph["n"])
    vertex_index: Dict[Vertex, int] = graph["vertex_index"]  # type: ignore[assignment]

    if target_index < 0 or target_index >= graph["vertex_count"]:
        raise IndexError("target_index out of range")

    base = graph["vertices"][target_index]
    attackers: List[int] = []
    seen: Set[Vertex] = set()

    def add_vertex(operations: Iterable[Tuple[int, int]]) -> None:
        vertex = base
        for left, right in operations:
            vertex = apply_transposition(vertex, left, right)
        if vertex in seen:
            return
        seen.add(vertex)
        attackers.append(vertex_index[vertex])

    for i in range(2, n, 2):
        add_vertex(((0, i - 1), (0, i)))

    for i in range(3, n - 2, 4):
        add_vertex(((i - 1, i), (i + 1, i + 2)))

    if n % 2 == 0:
        add_vertex(((0, n - 1), (n - 2, n - 1)))
    elif n % 4 == 1:
        add_vertex(((n - 3, n - 2), (n - 2, n - 1)))

    return attackers


def edge_attack_target_edges(graph: Dict[str, object], target_index: int) -> List[Tuple[int, int]]:
    """Pilih satu edge keluar dari setiap tetangga target untuk diserang.

    Setiap tetangga target memotong satu edge yang tidak terhubung ke target.
    Edge yang diserang dan kedua ujungnya akan dihapus dari graf.
    """
    if target_index < 0 or target_index >= graph["vertex_count"]:
        raise IndexError("target_index out of range")

    attacked_edges: Set[Tuple[int, int]] = set()

    for neighbor in graph["adjacency"][target_index]:
        candidates = [endpoint for endpoint in graph["adjacency"][neighbor] if endpoint != target_index]
        if not candidates:
            continue
        endpoint = min(candidates)
        attacked_edges.add(tuple(sorted((neighbor, endpoint))))

    return sorted(attacked_edges)


def vertex_attack(graph: Dict[str, object], target_index: int) -> Dict[str, object]:
    """Simulasi vertex attack pada target tertentu."""
    faulty_nodes = vertex_attack_fault_set(graph, target_index)
    removed_nodes = subversi_vertex(graph, faulty_nodes)
    remaining = [i for i in range(graph["vertex_count"]) if i not in removed_nodes]
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    return {
        "target": target_index,
        "faulty_nodes": faulty_nodes,
        "removed_nodes": sorted(list(removed_nodes)),
        "remaining_nodes": remaining,
        "result": analyze_remaining_graph(adjacency, remaining),
    }


def edge_attack(graph: Dict[str, object], target_index: int) -> Dict[str, object]:
    """Simulasi edge attack pada target tertentu."""
    attacked_edges = edge_attack_target_edges(graph, target_index)
    attacked_nodes = set()
    for a, b in attacked_edges:
        attacked_nodes.add(a)
        attacked_nodes.add(b)

    remaining = [i for i in range(graph["vertex_count"]) if i not in attacked_nodes]
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    return {
        "target": target_index,
        "attacked_edges": attacked_edges,
        "attacked_nodes": sorted(list(attacked_nodes)),
        "remaining_nodes": remaining,
        "result": analyze_remaining_graph(adjacency, remaining),
    }


# Penjelasan: Simulasi edge subversion murni
def simulasi_edge_subversion_murni(graph: Dict[str, object], edges_target: List[Tuple[int, int]]) -> Tuple[Set[int], Set[Tuple[int, int]]]:
    """Simulasi serangan edge dengan menghapus node endpoint dan edge terpengaruh.
    
    Return: (removed_nodes, affected_edges)
    """
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    vertex_count: int = graph["vertex_count"]  # type: ignore[assignment]
    
    nodes_terserang = set()
    for u, v in edges_target:
        nodes_terserang.add(u)
        nodes_terserang.add(v)
    
    edges_kedampak = set()
    for u in range(vertex_count):
        for v in adjacency[u]:
            if u < v:
                edge_aktif = (u, v)
                if u in nodes_terserang or v in nodes_terserang:
                    edges_target_sorted = [(e1, e2) if e1 < e2 else (e2, e1) for e1, e2 in edges_target]
                    if edge_aktif not in edges_target_sorted:
                        edges_kedampak.add(edge_aktif)
    
    return nodes_terserang, edges_kedampak


# Penjelasan: Menghasilkan ringkasan lengkap analisis graf BSn
def graph_summary(n: int) -> Dict[str, object]:
    """Membuat ringkasan statistik lengkap untuk graf BSn dengan dimensi n.
    
    Output mencakup:
    - Jumlah vertex dan edge
    - Degree setiap vertex
    - Kappa (vertex connectivity) teoritis dan eksak
    - Cut set berdasarkan teorema dan analisis eksak
    - Simulasi vertex subversion (dari nodes.py)
    - Simulasi edge subversion (dari edges.py)
    """
    graph = build_bsn(n)
    theorem_cut = theorem_cut_set(graph)
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    removed = closed_neighborhood(adjacency, theorem_cut)
    remaining = [index for index in range(int(graph["vertex_count"])) if index not in removed]
    theorem_reason = analyze_remaining_graph(adjacency, remaining)
    exact = exact_kappa_nb(graph)
    exact_lambda = exact_lambda_nb(graph)
    
    # Simulasi vertex subversion (dari nodes.py)
    node_penyerang = cari_node_penyerang_otomatis(n, graph)
    nodes_terhapus_vertex = subversi_vertex(graph, node_penyerang)
    remaining_vertex = [i for i in range(int(graph["vertex_count"])) if i not in nodes_terhapus_vertex]
    vertex_subversion_result = analyze_remaining_graph(adjacency, remaining_vertex)
    
    # Simulasi edge subversion (dari edges.py)
    if len(remaining_vertex) > 0:
        target_node = 0
        neighbor_edges = []
        for neighbor in adjacency[target_node]:
            neighbor_edges.append((target_node, neighbor))
        
        if len(neighbor_edges) > 0:
            nodes_terserang_edge, edges_kedampak = simulasi_edge_subversion_murni(graph, neighbor_edges[:int(graph["theoretical_lambda_nb"])])
            remaining_edge = [i for i in range(int(graph["vertex_count"])) if i not in nodes_terserang_edge]
            edge_subversion_result = analyze_remaining_graph(adjacency, remaining_edge)
        else:
            nodes_terserang_edge = set()
            edges_kedampak = set()
            edge_subversion_result = "connected"
    else:
        nodes_terserang_edge = set()
        edges_kedampak = set()
        edge_subversion_result = "empty"

    return {
        "n": n,
        "vertex_count": graph["vertex_count"],
        "edge_count": graph["edge_count"],
        "degree": graph["degree"],
        "kappa_nb_theorem": graph["theoretical_kappa_nb"],
        "lambda_nb_theorem": graph["theoretical_lambda_nb"],
        "theorem_cut_size": len(theorem_cut),
        "theorem_cut_vertices": [graph["vertices"][index] for index in theorem_cut],  # type: ignore[index]
        "theorem_subversion_result": theorem_reason,
        "exact_kappa_nb": None
        if exact is None
        else {
            "k": exact["k"],
            "reason": exact["reason"],
            "cut_vertices": [graph["vertices"][index] for index in exact["cut_set"]],  # type: ignore[index]
        },
        "exact_lambda_nb": None
        if exact_lambda is None
        else {
            "k": exact_lambda["k"],
            "reason": exact_lambda["reason"],
            "cut_edges": [(edge[0], edge[1]) for edge in exact_lambda["cut_edges"]],
        },
        "vertex_subversion_simulation": {
            "attacker_nodes_count": len(node_penyerang),
            "removed_nodes_count": len(nodes_terhapus_vertex),
            "remaining_nodes_count": len(remaining_vertex),
            "result": vertex_subversion_result,
        },
        "edge_subversion_simulation": {
            "attacked_nodes_count": len(nodes_terserang_edge),
            "affected_edges_count": len(edges_kedampak),
            "remaining_nodes_count": len(remaining_edge),
            "result": edge_subversion_result,
        },
    }


# Penjelasan: Fungsi utama untuk menjalankan program dan output hasil analisis
def simulate_bsn_subversion(n: int) -> None:
    """Menjalankan simulasi vertex dan edge subversion untuk graf BSn.
    
    Output mencakup:
    - Graf normal
    - Graf dengan serangan vertex (seperti nodes.py)
    - Graf dengan serangan edge (seperti edges.py)
    - Analisis hasil serangan
    """
    graph = build_bsn(n)
    
    print(f"\n{'='*60}")
    print(f"BUBBLE-SORT STAR GRAPH BS{n} - SUBVERSION SIMULATION")
    print(f"{'='*60}")
    print(f"\nGraf Properties:")
    print(f"  - Vertex Count: {graph['vertex_count']}")
    print(f"  - Edge Count: {graph['edge_count']}")
    print(f"  - Degree: {graph['degree']}")
    print(f"  - Theoretical Kappa (κ): {graph['theoretical_kappa_nb']}")
    print(f"  - Theoretical Lambda (λ): {graph['theoretical_lambda_nb']}")
    
    # Simulasi Vertex Subversion (seperti nodes.py)
    print(f"\n{'-'*60}")
    print("VERTEX SUBVERSION SIMULATION (dari nodes.py)")
    print(f"{'-'*60}")
    
    node_penyerang = cari_node_penyerang_otomatis(n, graph)
    nodes_terhapus = subversi_vertex(graph, node_penyerang)
    remaining_vertex = [i for i in range(int(graph["vertex_count"])) if i not in nodes_terhapus]
    
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    vertex_result = analyze_remaining_graph(adjacency, remaining_vertex)
    
    print(f"Attacker Nodes: {len(node_penyerang)}")
    print(f"Removed Nodes (including neighbors): {len(nodes_terhapus)}")
    print(f"Remaining Nodes: {len(remaining_vertex)}")
    print(f"Graph Status: {vertex_result}")
    print(f"Graph Connected: {vertex_result != 'disconnected' and vertex_result != 'empty'}")
    
    # Simulasi Edge Subversion (seperti edges.py)
    print(f"\n{'-'*60}")
    print("EDGE SUBVERSION SIMULATION (dari edges.py)")
    print(f"{'-'*60}")
    
    target_node = 0
    neighbor_edges = []
    for neighbor in adjacency[target_node]:
        neighbor_edges.append((target_node, neighbor))
    
    max_edges = int(graph["theoretical_lambda_nb"])
    edges_target = neighbor_edges[:max_edges]
    
    nodes_terserang, edges_kedampak = simulasi_edge_subversion_murni(graph, edges_target)
    remaining_edge = [i for i in range(int(graph["vertex_count"])) if i not in nodes_terserang]
    edge_result = analyze_remaining_graph(adjacency, remaining_edge)
    
    print(f"Target Edges Attacked: {len(edges_target)}")
    print(f"Attacked Endpoint Nodes: {len(nodes_terserang)}")
    print(f"Affected Edges (collateral): {len(edges_kedampak)}")
    print(f"Remaining Nodes: {len(remaining_edge)}")
    print(f"Graph Status: {edge_result}")
    print(f"Graph Connected: {edge_result != 'disconnected' and edge_result != 'empty'}")
    
    # Teorema Cut Set (dari theorem)
    print(f"\n{'-'*60}")
    print("THEOREM-BASED CUT SET ANALYSIS")
    print(f"{'-'*60}")
    
    theorem_cut = theorem_cut_set(graph)
    removed_theorem = closed_neighborhood(adjacency, theorem_cut)
    remaining_theorem = [i for i in range(int(graph["vertex_count"])) if i not in removed_theorem]
    theorem_result = analyze_remaining_graph(adjacency, remaining_theorem)
    
    print(f"Theorem Cut Set Size: {len(theorem_cut)}")
    print(f"Removed Nodes (including neighbors): {len(removed_theorem)}")
    print(f"Remaining Nodes: {len(remaining_theorem)}")
    print(f"Graph Status: {theorem_result}")
    print(f"Graph Connected: {theorem_result != 'disconnected' and theorem_result != 'empty'}")
    
    print(f"\n{'='*60}\n")


def main() -> None:
    """Program utama untuk menganalisis dan menampilkan statistik graf BSn.
    
    Usage:
        python bsn_logic.py --n 6 --pretty
        python bsn_logic.py --n 4 --simulate
    """
    parser = argparse.ArgumentParser(
        description="Reference logic for Bubble-Sort Star Graph BSn."
    )
    parser.add_argument("--n", type=int, default=6, help="Dimension n for BSn.")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON summary.",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run vertex and edge subversion simulations.",
    )
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("n must be at least 2")

    if args.simulate:
        simulate_bsn_subversion(args.n)
    else:
        summary = graph_summary(args.n)
        print(
            json.dumps(
                summary,
                indent=2 if args.pretty else None,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
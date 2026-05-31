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


# Penjelasan: Menghasilkan ringkasan lengkap analisis graf BSn
def graph_summary(n: int) -> Dict[str, object]:
    """Membuat ringkasan statistik lengkap untuk graf BSn dengan dimensi n.
    
    Output mencakup:
    - Jumlah vertex dan edge
    - Degree setiap vertex
    - Kappa (vertex connectivity) teoritis dan eksak
    - Cut set berdasarkan teorema dan analisis eksak
    """
    graph = build_bsn(n)
    theorem_cut = theorem_cut_set(graph)
    adjacency: List[Set[int]] = graph["adjacency"]  # type: ignore[assignment]
    removed = closed_neighborhood(adjacency, theorem_cut)
    remaining = [index for index in range(int(graph["vertex_count"])) if index not in removed]
    theorem_reason = analyze_remaining_graph(adjacency, remaining)
    exact = exact_kappa_nb(graph)
    exact_lambda = exact_lambda_nb(graph)

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
    }


# Penjelasan: Fungsi utama untuk menjalankan program dan output hasil analisis
def main() -> None:
    """Program utama untuk menganalisis dan menampilkan statistik graf BSn.
    
    Usage:
        python bsn_logic.py --n 6 --pretty
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
    args = parser.parse_args()

    if args.n < 2:
        raise SystemExit("n must be at least 2")

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
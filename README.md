# Visiualisasi SDA - Bubble-Sort Star Graph (BSn)

Proyek ini adalah implementasi analisis graf untuk struktur Bubble-Sort Star (BSn). Tujuannya adalah membangun graf BSn, menghitung structural properties seperti jumlah vertex/edge, degree, dan menganalisis connectivity baik secara teoretis maupun eksak.

## Deskripsi Proyek

Graf `BSn` adalah graf yang dibangun dari semua permutasi `1..n` sebagai vertex. Setiap vertex terhubung dengan dua jenis edge:

- `bubble`: transposisi dua elemen bersebelahan pada posisi `i` dan `i+1`
- `star`: transposisi elemen pertama dengan elemen lain

Proyek ini mengandung logika untuk:

- menghasilkan seluruh vertex untuk dimensi `n`
- membangun adjacency graph BSn
- menghitung cut set berdasarkan teorema tertentu untuk BSn
- menganalisis closed neighborhood dan sisa graf setelah penghapusan vertex
- menghitung vertex connectivity (`kappa`) dan edge connectivity (`lambda`) secara eksak untuk graf kecil

## Struktur File

- `bsn_logic.py` : inti logika graf BSn.
- `edges.py` : file kosong saat ini, dapat dipakai untuk definisi edge tambahan atau fungsi pendukung di masa depan.
- `preview (1).html` : kemungkinan file tampilan visual untuk graf atau hasil output.
- `graphviz (1).png`, `graphviz (2).png` : gambar hasil visualisasi graf.

## Cara Menjalankan

Gunakan Python 3 untuk menjalankan file `bsn_logic.py`.

```bash
python bsn_logic.py --n 6 --pretty
```

Pilihan:

- `--n`: dimensi graf BSn, minimal `2`
- `--pretty`: mencetak JSON dengan indentasi agar mudah dibaca

Contoh output ringkas:

```json
{
  "n": 6,
  "vertex_count": 720,
  "edge_count": 1656,
  "degree": 9,
  "kappa_nb_theorem": 4,
  "lambda_nb_theorem": 9,
  "theorem_cut_size": 3,
  "theorem_cut_vertices": [ ... ],
  "theorem_subversion_result": "disconnected",
  "exact_kappa_nb": null,
  "exact_lambda_nb": null
}
```

> Untuk nilai `n` besar, perhitungan eksak `kappa` dan `lambda` akan sangat lambat atau tidak tersedia karena kompleksitas kombinatorial.

## Penjelasan Fungsi Utama di `bsn_logic.py`

- `generate_vertices(n)`: menghasilkan semua permutasi vertex untuk `n`
- `apply_transposition(vertex, left, right)`: menukar dua posisi dalam sebuah permutasi
- `build_bsn(n)`: membangun graf BSn dengan adjacency list
- `theorem_cut_set(graph)`: membentuk cut set berdasarkan operasi transposisi tertentu
- `closed_neighborhood(adjacency, seed_set)`: menghitung neighbor tertutup dari set vertex
- `analyze_remaining_graph(adjacency, remaining)`: menentukan apakah graf yang tersisa `empty`, `complete`, `connected`, atau `disconnected`
- `exact_kappa_nb(graph)`: mencari nilai kappa eksak untuk graf kecil
- `exact_lambda_nb(graph)`: mencari nilai lambda eksak untuk graf kecil
- `graph_summary(n)`: menyusun ringkasan statistik graf BSn
- `main()`: parser argumen dan output JSON

## Catatan

- Jika kamu ingin mengembangkan visualisasi, file `preview (1).html` dapat dijadikan basis tampilan.
- `edges.py` masih kosong dan bisa diisi dengan helper atau utilitas graf tambahan.
- Gunakan `git add README.md`, `git commit -m "Add README"`, dan `git push` untuk mengunggah README ke GitHub.

# BSn Graph Visualization - Integration Guide

## ✅ Sistem Sudah Nyambung!

Python logic (`bsn_logic.py`) sekarang connected ke HTML via Flask backend.

---

## 🚀 Cara Menjalankan

### Terminal 1: Run Flask Backend
```bash
cd c:\Users\victus\Downloads\VisiualisasiSDA
python app.py
```

Output yang diharapkan:
```
============================================================
BSn Graph Visualization Backend
============================================================

✓ Flask server starting on http://localhost:5000

API Endpoints:
  GET  /api/graph/<n>
  GET  /api/theorem-cut/<n>
  GET  /api/exact-kappa/<n>
  GET  /api/exact-lambda/<n>
  GET  /api/vertex-subversion/<n>
  GET  /api/edge-subversion/<n>
  GET  /api/summary/<n>

============================================================

 * Running on http://127.0.0.1:5000
```

### Terminal 2: Open HTML
```bash
# Windows
start preview.html

# atau buka manual di browser
http://localhost:5000/
```

---

## 📡 API Reference

### 1. **Build Graph**
```
GET /api/graph/<n>
```
Membangun graf BSn dengan n dimensi.

**Response:**
```json
{
  "n": 4,
  "vertex_count": 24,
  "edge_count": 60,
  "degree": 5,
  "theoretical_kappa_nb": 2,
  "theoretical_lambda_nb": 5,
  "vertices": [[1,2,3,4], [1,2,4,3], ...],
  "adjacency": [[1,2,6,14,21], [...], ...],
  "edges": [{"a": 0, "b": 1}, ...]
}
```

---

### 2. **Theorem Cut Set**
```
GET /api/theorem-cut/<n>
```
Dapatkan cut set berdasarkan teorema.

**Response:**
```json
{
  "cut_set": [5, 12],
  "removed_nodes": [5, 12, 8, 15, 20, ...],
  "remaining_nodes": [1, 3, 7, 9, ...],
  "result": "disconnected",
  "cut_set_size": 2,
  "removed_count": 10
}
```

---

### 3. **Exact Kappa (Vertex Connectivity)**
```
GET /api/exact-kappa/<n>
```
Hitung kappa eksak (hanya untuk n ≤ 5).

**Response:**
```json
{
  "k": 2,
  "cut_set": [0, 5],
  "removed": [0, 5, 1, 2, 3, ...],
  "remaining": [7, 8, 9, ...],
  "reason": "disconnected"
}
```

---

### 4. **Exact Lambda (Edge Connectivity)**
```
GET /api/exact-lambda/<n>
```
Hitung lambda eksak (hanya untuk n ≤ 5).

**Response:**
```json
{
  "k": 5,
  "cut_edges": [[0,1], [0,2], [0,6], [0,14], [0,21]],
  "reason": "disconnected"
}
```

---

### 5. **Vertex Subversion (dari nodes.py)**
```
GET /api/vertex-subversion/<n>
```
Simulasi vertex attack dengan attacker nodes.

**Response:**
```json
{
  "attacker_nodes": [5, 12],
  "removed_nodes": [5, 12, 1, 3, 8, ...],
  "remaining_nodes": [2, 4, 6, 7, ...],
  "result": "connected",
  "attacker_count": 2,
  "removed_count": 9
}
```

---

### 6. **Edge Subversion (dari edges.py)**
```
GET /api/edge-subversion/<n>
```
Simulasi edge attack.

**Response:**
```json
{
  "attacked_edges": [[0,1], [0,2], [0,6], [0,14], [0,21]],
  "attacked_nodes": [0, 1, 2, 6, 14, 21],
  "affected_edges": [[1,4], [2,8], ...],
  "remaining_nodes": [3, 5, 7, ...],
  "result": "connected",
  "attacked_edge_count": 5,
  "attacked_node_count": 6
}
```

---

### 7. **Complete Summary**
```
GET /api/summary/<n>
```
Dapatkan ringkasan lengkap semua analisis.

**Response:**
```json
{
  "n": 4,
  "vertex_count": 24,
  "edge_count": 60,
  "degree": 5,
  "theoretical_kappa": 2,
  "theoretical_lambda": 5,
  "theorem_cut": {
    "size": 2,
    "nodes": [5, 12],
    "removed_count": 10,
    "result": "disconnected"
  },
  "exact_kappa": {
    "k": 2,
    "result": "disconnected"
  },
  "exact_lambda": {
    "k": 5,
    "result": "disconnected"
  },
  "vertex_subversion": {
    "attacker_count": 2,
    "removed_count": 9,
    "result": "connected"
  },
  "edge_subversion": {
    "attacked_edges": 5,
    "attacked_nodes": 6,
    "result": "connected"
  }
}
```

---

## 🔧 Cara Kerja Integrasi

### Backend (Python)
```
app.py (Flask Server)
  ↓
bsn_logic.py (Main Logic)
  ├─ build_bsn()
  ├─ theorem_cut_set()
  ├─ exact_kappa_nb()
  ├─ exact_lambda_nb()
  ├─ cari_node_penyerang_otomatis()
  ├─ subversi_vertex()
  └─ simulasi_edge_subversion_murni()
```

### Frontend (HTML)
```
preview.html (3D Visualization)
  ↓
buildBSnData() - Call /api/graph/<n>
  ↓
computeKappaNB() - Call /api/exact-kappa/<n>
  ↓
computeLambdaNB() - Call /api/exact-lambda/<n>
  ↓
buildTheoremCutSet() - Call /api/theorem-cut/<n>
  ↓
REST API (Synchronous XMLHttpRequest)
```

---

## 📊 Contoh Penggunaan

### Test di Terminal
```bash
# Test graph build
curl http://localhost:5000/api/graph/4

# Test theorem cut
curl http://localhost:5000/api/theorem-cut/5

# Test vertex subversion
curl http://localhost:5000/api/vertex-subversion/4

# Test edge subversion
curl http://localhost:5000/api/edge-subversion/4

# Test summary
curl http://localhost:5000/api/summary/4
```

---

## ⚙️ File Structure

```
VisiualisasiSDA/
├── bsn_logic.py           ← Python main logic (updated)
├── app.py                 ← Flask backend (NEW)
├── preview (1).html       ← 3D visualization (updated)
├── nodes (1).py           ← Reference implementation
├── edges (1) (1).py       ← Reference implementation
└── README.md              ← This file
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to backend"
- Pastikan Flask server sudah running di terminal 1
- Cek apakah port 5000 tidak terpakai

### Error: Graph tidak muncul di HTML
- Buka browser console (F12) untuk lihat error messages
- Cek apakah backend mengembalikan data JSON valid

### Error: "n must be between 2 and 8"
- n terlalu besar atau terlalu kecil
- Backend hanya support n = 2 hingga 8

---

## 📝 Notes

- **Synchronous XMLHttpRequest**: HTML menggunakan sync requests untuk simplicity
- **CORS Enabled**: Flask backend enable CORS untuk allow requests dari HTML
- **Default n=4**: HTML default value untuk BSn graph
- **Max n=8**: Backend limit untuk performa
- **Exact computation n≤5**: Brute force methods hanya untuk n kecil

---

## 🎯 Next Steps

1. Run Flask server: `python app.py`
2. Open HTML: `http://localhost:5000/`
3. Build graph dengan dimension n
4. Click node untuk select target
5. Test simulasi failures
6. Lihat analisis hasil di panel kiri

---

**Selamat! System sudah fully integrated! 🎉**

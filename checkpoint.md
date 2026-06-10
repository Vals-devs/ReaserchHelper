# Checkpoint — ResearchFinder

> **Last updated:** June 2026
> **Status:** Development (local running, not yet deployed)

---

## 1. Ringkasan Project

**ResearchFinder** adalah platform web untuk membantu mahasiswa Indonesia menemukan, memahami, dan mengelola paper ilmiah menggunakan AI. Project ini dibangun berdasarkan brief di `project-brief-researchfinder.md`.

---

## 2. Tech Stack (yang sudah berjalan)

| Layer | Teknologi | Status |
|-------|-----------|--------|
| Frontend | Vue 3 + TypeScript + Vite | ✅ Jalan |
| Styling | Tailwind CSS v4 | ✅ Jalan |
| State | Pinia (5 stores) | ✅ Jalan |
| Routing | Vue Router 4 | ✅ Jalan |
| Backend | FastAPI (Python 3.10) | ✅ Jalan |
| Database | SQLite (dev) / PostgreSQL (Docker) | ✅ Jalan |
| Cache | Redis (disabled di dev) | ⚙️ Configured |
| AI | Groq API (LLaMA 3.1 8B + LLaMA 3.3 70B) | ✅ Jalan |
| Paper API | Semantic Scholar + arXiv | ✅ Jalan |
| PDF | PyMuPDF | ✅ Jalan |
| Deploy | Docker Compose + Nginx | 📋 Configured (belum dipakai) |

---

## 3. Fitur yang Sudah Selesai

### 3.1 Autentikasi ✅
- Register (nama, email, password, institusi)
- Login dengan JWT
- Auth guard di semua route frontend
- Error handling (email duplikat, password salah, server error)
- **Files:** `routers/auth.py`, `views/auth/Login.vue`, `views/auth/Register.vue`, `stores/auth.ts`

### 3.2 Paper Search ✅
- Search dari Semantic Scholar + arXiv secara concurrent
- Deduplikasi hasil berdasarkan DOI dan judul
- Filter: sumber (semua/S2/arXiv), bidang studi
- Auto-cache paper ke database
- Auto-save ke search history
- Rate limiting Semantic Scholar (1 req/detik didukung `asyncio.Lock` untuk mencegah concurrency race condition)
- Caching pencarian (In-Memory TTL Cache) untuk meminimalkan beban request ke Semantic Scholar
- Auto-retry 429 rate limit error dengan toleransi jeda waktu
- Error handling untuk kedua API
- **Files:** `routers/papers.py`, `services/semantic_scholar.py`, `services/arxiv.py`, `views/Search.vue`, `stores/papers.ts`

### 3.3 Paper Detail ✅
- Tampil: judul, authors, tahun, DOI, citation count, abstract, field tags
- Source badge (Semantic Scholar / arXiv / Uploaded)
- **Files:** `views/PaperDetail.vue`

### 3.4 AI Features ✅

| Feature | Endpoint | Model | Status |
|---------|----------|-------|--------|
| AI Summarize | `POST /api/ai/summarize` | LLaMA 3.1 8B | ✅ Jalan |
| Translate Abstract | `POST /api/ai/translate` | LLaMA 3.1 8B | ✅ Jalan |
| Explain Text | `POST /api/ai/explain` | LLaMA 3.1 8B | ✅ Jalan |
| Gap Analysis | `POST /api/ai/gap-analysis` | LLaMA 3.3 70B | ✅ Jalan |
| Find Related | `GET /api/papers/{id}/related` | S2 Recommendations + Groq fallback | ✅ Jalan |
| Suggest Related | `POST /api/ai/suggest-related` | Groq + S2 Search | ✅ Jalan |

- JSON response parsing robust (handle markdown fences, nested JSON)
- System prompt engineering untuk output terstruktur
- **Files:** `services/groq.py`, `routers/ai.py`, `stores/ai.ts`

### 3.5 PDF Upload ✅
- Upload PDF → extract text dengan PyMuPDF
- AI extract metadata otomatis (judul, authors, tahun, abstrak)
- Simpan PDF ke `backend/uploads/`
- List dan delete uploaded papers
- Proteksi duplikasi upload berdasarkan pencocokan judul paper secara case-insensitive
- 40+ PDF sudah ter-upload di database
- **Files:** `routers/upload.py`, `services/pdf_parser.py`, `stores/upload.ts`

### 3.6 Collections ✅
- CRUD collections (create, read, update, delete)
- Tambah paper ke koleksi dari PaperDetail page
- Hapus paper dari koleksi
- Notes per paper dalam koleksi
- Paper count per koleksi
- Get collection detail dengan full paper data (JOIN)
- Duplicate check saat menambah paper
- **Files:** `routers/collections.py`, `views/Collections.vue`, `views/CollectionDetail.vue`, `stores/collections.ts`

### 3.7 Research Gap Analysis ✅
- Pilih 3-10 paper dari **multiple sources**:
  - Uploaded PDFs
  - Semua collections
  - Collection tertentu (filter)
- Deduplikasi otomatis (paper yang sama di upload + koleksi)
- Source badge per paper card
- Select all / Reset buttons
- Hasil analisis 4 section: topik dominan, metodologi, celah penelitian, saran topik
- **Files:** `views/GapAnalysis.vue`, `stores/upload.ts`, `stores/collections.ts`

### 3.8 Search History ✅
- Auto-save setiap search ke database
- List semua riwayat pencarian
- "Cari Lagi" button → redirect ke search dengan query yang sama
- Hapus per-item atau hapus semua
- Format tanggal Indonesia
- **Files:** `routers/history.py`, `views/History.vue`

---

## 4. Cara Menjalankan (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 20+
- Groq API key (sudah di `.env`)
- Semantic Scholar API key (sudah di `.env`)

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/api/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
- App: http://localhost:5173
- Proxy `/api` → `http://localhost:8000` (configured di `vite.config.ts`)

### Environment Files
- `backend/.env` — SQLite + API keys (untuk local dev)
- `.env` (root) — PostgreSQL + API keys (untuk Docker Compose)

---

## 5. Database Schema (SQLite - 7 tabel)

| Tabel | Fungsi |
|-------|--------|
| `users` | Data user (id, name, email, password, institution) |
| `papers` | Cache paper dari S2/arXiv/upload (id, title, authors, abstract, full_text, citation_count) |
| `ai_summaries` | Cache hasil AI summarize |
| `collections` | Koleksi user (id, name, description, is_public) |
| `collection_papers` | Relasi koleksi-paper + notes + highlights |
| `search_history` | Riwayat pencarian user |
| *(uploads/)* | Folder file PDF yang di-upload |

---

## 6. API Endpoints (28 routes)

```
Auth:
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/me
  PUT  /api/auth/profile

Papers:
  GET  /api/papers/search?q=&source=&field=&year_from=&year_to=
  GET  /api/papers/{id}
  GET  /api/papers/{id}/related

Collections:
  GET  /api/collections/                  (+ paper_count)
  POST /api/collections/
  GET  /api/collections/{id}              (+ full papers data)
  PUT  /api/collections/{id}
  DELETE /api/collections/{id}
  POST /api/collections/{id}/papers
  DELETE /api/collections/{id}/papers/{paper_id}
  PUT  /api/collections/{id}/papers/{paper_id}/notes

AI:
  POST /api/ai/summarize
  POST /api/ai/translate
  POST /api/ai/explain
  POST /api/ai/gap-analysis
  POST /api/ai/suggest-related

Upload:
  POST /api/upload/pdf
  GET  /api/upload/papers
  DELETE /api/upload/{id}

History:
  GET    /api/history/
  DELETE /api/history/{id}
  DELETE /api/history/

Bibliography:
  POST /api/bibliography/generate

Health:
  GET  /api/health
```

---

## 7. Frontend Pages (9 views)

| Route | View | Status |
|-------|------|--------|
| `/login` | Login.vue | ✅ |
| `/register` | Register.vue | ✅ |
| `/` | Dashboard.vue | ✅ (stats placeholder) |
| `/search` | Search.vue | ✅ |
| `/papers/:id` | PaperDetail.vue | ✅ |
| `/collections` | Collections.vue | ✅ |
| `/collections/:id` | CollectionDetail.vue | ✅ |
| `/gap-analysis` | GapAnalysis.vue | ✅ |
| `/history` | History.vue | ✅ |

---

## 8. UI Design Mockups

7 file mockup interaktif di folder `designs/` (Qoder Canvas format):
- `layout.canvas.tsx` — Global layout + sidebar
- `auth.canvas.tsx` — Login + Register
- `search.canvas.tsx` — Search page + paper cards
- `paper-detail.canvas.tsx` — Detail + AI summary panel
- `collections.canvas.tsx` — Collections grid + detail
- `gap-analysis.canvas.tsx` — Upload + select + results
- `history.canvas.tsx` — Search history list

---

## 9. Yang Belum Dikerjakan

| Item | Priority | Notes |
|------|----------|-------|
| Bibliography Export (APA/IEEE/Chicago) | High | Router sudah ada, logic format belum diimplementasi |
| Docker Compose deployment | Medium | Config sudah ada, belum pernah dijalankan |
| Dashboard real stats | Low | Masih placeholder, perlu query aggregasi |
| Browser extension | Low | Nice-to-have dari brief |
| Citation network visualizer | Low | Nice-to-have dari brief |
| Collaboration (share koleksi) | Low | Nice-to-have dari brief |
| Weekly digest email | Low | Nice-to-have dari brief |
| Unit tests | Medium | Belum ada test sama sekali |
| Production build (nginx serve static) | Medium | Config ada, belum dipakai |

---

## 10. Known Issues / Limitations

1. **Model Groq** — `gemma2-9b-it` sudah decommissioned, diganti ke `llama-3.3-70b-versatile` (Sudah teratasi)
2. **Rate limit Groq** — Free tier, bisa kena 429 jika terlalu banyak request berurutan (Sudah dimitigasi dengan auto-retry + exponential backoff)
3. **SQLite concurrency** — Tidak cocok untuk production (gunakan PostgreSQL via Docker)
4. **Redis** — Disabled di dev, cache belum aktif
5. **PDF text extraction** — Tidak bisa extract dari PDF scan/image (hanya text-based PDF)
6. **Upload duplicates** — Bisa upload PDF yang sama berkali-kali (Sudah teratasi dengan validasi judul paper case-insensitive saat upload)

---

## 11. Struktur File Penting

```
ReaserchHelper/
├── project-brief-researchfinder.md   ← Brief asli
├── checkpoint.md                      ← File ini
├── docker-compose.yml                 ← Docker orchestration
├── nginx.conf                         ← Reverse proxy config
├── .env                               ← Env vars (Docker)
│
├── backend/
│   ├── .env                           ← Env vars (local dev)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── researchfinder.db              ← SQLite database
│   ├── uploads/                       ← PDF files
│   └── app/
│       ├── main.py                    ← FastAPI entry + CORS + 7 routers
│       ├── core/
│       │   ├── config.py              ← Pydantic settings
│       │   ├── database.py            ← SQLAlchemy async engine
│       │   ├── security.py            ← JWT + bcrypt
│       │   └── cache.py               ← Redis helpers
│       ├── routers/                   ← 7 API routers
│       ├── models/                    ← 4 SQLAlchemy models (6 tabel)
│       ├── schemas/                   ← Pydantic schemas
│       └── services/                  ← External API wrappers
│           ├── groq.py                ← AI (summarize, translate, explain, gap analysis)
│           ├── semantic_scholar.py    ← Paper search + recommendations
│           ├── arxiv.py               ← arXiv paper search
│           ├── pdf_parser.py          ← PyMuPDF text extraction
│           ├── bibliography.py        ← Format APA/IEEE/Chicago
│           └── crossref.py            ← DOI metadata
│
├── frontend/
│   ├── vite.config.ts                 ← Vite + Tailwind + proxy
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── App.vue                    ← Root + sidebar layout
│       ├── main.ts                    ← Entry point
│       ├── router/index.ts            ← 9 routes + auth guard
│       ├── services/api.ts            ← Axios + JWT interceptor
│       ├── stores/                    ← 5 Pinia stores
│       ├── components/ui/             ← AppSidebar.vue
│       └── views/                     ← 9 page views
│
└── designs/                           ← 7 Canvas mockup files
```

---

## 12. API Keys yang Sudah Terdaftar

| Service | Key | Rate Limit |
|---------|-----|------------|
| Groq | `gsk_9BLq...` | Free tier |
| Semantic Scholar | `s2k-WeZl...` | 1 req/sec |
| Unpaywall | Email-based | Unlimited |

---

*Checkpoint ini dibuat sebagai referensi untuk melanjutkan development di session berikutnya.*

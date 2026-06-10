# 📋 Project Brief — AI-Powered Research Paper Finder & Summarizer

> **Status:** Planning Phase  
> **Author:** Ival Permana  
> **Dibuat:** Juni 2026  
> **Estimasi Durasi:** 6–8 minggu

---

## 1. Overview

Platform riset akademik berbasis web yang membantu mahasiswa — terutama yang sedang mengerjakan skripsi, tugas akhir, atau riset — menemukan, memahami, dan mengelola paper ilmiah dengan lebih efisien. Menggunakan AI untuk menyederhanakan paper yang kompleks menjadi ringkasan yang mudah dipahami, mengidentifikasi celah penelitian, dan memformat referensi secara otomatis.

Platform ini memanfaatkan **API publik gratis** (Semantic Scholar, arXiv) sebagai sumber data paper sehingga tidak membutuhkan biaya apapun untuk data.

Project ini ditujukan sebagai:
- **Portofolio freelance** yang menunjukkan kemampuan fullstack + AI + external API integration
- **Tool yang benar-benar berguna** untuk komunitas mahasiswa Indonesia
- **Learning project** untuk Python FastAPI, Groq API, dan integrasi external API
- Berpotensi menjadi **bahan paper/jurnal akademik** jika dikembangkan lebih lanjut

---

## 2. Tech Stack

### Frontend
| Teknologi | Versi | Kegunaan |
|---|---|---|
| Vue.js | 3.x | Framework utama frontend |
| Tailwind CSS | v4 | Styling & utility classes |
| Pinia | Latest | State management |
| Vue Router | 4.x | Client-side routing |
| Axios | Latest | HTTP client ke backend |
| Chart.js | Latest | Visualisasi data & statistik paper |

### Backend Utama
| Teknologi | Versi | Kegunaan |
|---|---|---|
| FastAPI | Latest | Framework backend utama (Python) |
| Python | 3.11+ | Bahasa backend |
| SQLAlchemy | Latest | ORM untuk database |
| Alembic | Latest | Database migration |
| Pydantic | Latest | Schema validation |
| httpx | Latest | Async HTTP client untuk external API |

### AI Layer
| Teknologi | Kegunaan |
|---|---|
| Groq API | Summarizer, gap analysis, simplifikasi bahasa |
| Model: LLaMA 3.1 8B | Default — cepat untuk summarisasi pendek |
| Model: Gemma 2 9B | Untuk analisis panjang (gap analysis) |

### External API (Gratis)
| API | Kegunaan | Limit |
|---|---|---|
| Semantic Scholar API | Search & fetch paper metadata + abstract | 100 req/5 menit (tanpa key) / 1 req/detik (dengan key gratis) |
| arXiv API | Paper dari bidang sains, teknik, CS, matematika | Tidak ada limit ketat |
| CrossRef API | Fetch metadata lengkap via DOI | Gratis, unlimited |
| Unpaywall API | Cek apakah paper tersedia open access | Gratis dengan email |

### Database & Cache
| Teknologi | Kegunaan |
|---|---|
| PostgreSQL | Database utama |
| Redis | Cache hasil search & AI response |

### Infrastructure
| Teknologi | Kegunaan |
|---|---|
| Docker | Containerisasi semua service |
| Docker Compose | Orchestrate multi-container |
| Nginx | Reverse proxy |
| Homelab Server | Deployment target utama |

---

## 3. Fitur

### 3.1 Core Features (Wajib)

- [ ] **Autentikasi** — Register, Login, Logout (JWT)
- [ ] **Paper Search** — Cari paper dari Semantic Scholar + arXiv sekaligus dalam satu query
- [ ] **Paper Detail** — Tampilkan metadata lengkap: judul, author, tahun, abstrak, DOI, citation count
- [ ] **Koleksi / Library** — Simpan paper ke koleksi pribadi, buat folder/kategori
- [ ] **Catatan Pribadi** — Tambah highlight & catatan per paper
- [ ] **Export Bibliography** — Generate daftar pustaka format APA / IEEE / Chicago dari koleksi
- [ ] **Riwayat Pencarian** — Simpan history search untuk referensi cepat

### 3.2 AI Features (Utama)

- [ ] **AI Paper Summarizer**
  - Input: abstrak + judul paper (atau full text jika tersedia)
  - Output: ringkasan 3–5 kalimat dalam **bahasa Indonesia** yang mudah dipahami
  - Dilengkapi: poin-poin kunci (key findings), metodologi singkat, kontribusi utama
  - Powered by: Groq API (LLaMA 3.1 8B)

- [ ] **Research Gap Analyzer**
  - User pilih 3–10 paper dari koleksinya
  - AI analisis kesamaan topik, metodologi, dan temuan antar paper
  - Output: identifikasi **celah penelitian** yang belum dieksplorasi
  - Berguna untuk: mahasiswa yang sedang mencari topik skripsi/tesis
  - Powered by: Groq API (Gemma 2 9B — model lebih panjang)

- [ ] **Plain Language Explainer**
  - User paste teks bagian paper yang tidak dimengerti
  - AI jelaskan dalam bahasa sederhana seperti menjelaskan ke teman
  - Support bahasa Indonesia & Inggris
  - Powered by: Groq API

- [ ] **Related Paper Suggester**
  - Dari paper yang sedang dilihat, AI sarankan topik pencarian lanjutan
  - Kombinasi: keyword extraction dari abstrak + query ke Semantic Scholar
  - Output: 5–10 paper relevan yang mungkin terlewat
  - Powered by: Groq API untuk keyword extraction + Semantic Scholar API

### 3.3 Nice to Have (Opsional)

- [ ] Upload PDF paper lokal → AI summarize isi lengkapnya (pakai PyMuPDF)
- [ ] Collaboration — share koleksi paper dengan teman/kelompok riset
- [ ] Citation network visualizer — graph hubungan antar paper
- [ ] Browser extension — simpan paper langsung dari Google Scholar
- [ ] Weekly digest — AI kirim email ringkasan paper terbaru sesuai minat riset

---

## 4. Arsitektur Sistem

```
┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                      │
│               Vue.js 3 + Tailwind v4                 │
└────────────────────────┬────────────────────────────┘
                         │ HTTP / REST API
┌────────────────────────▼────────────────────────────┐
│                  NGINX (Reverse Proxy)               │
│          /api  →  FastAPI     /  →  Vue SPA          │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│               FastAPI Backend (Port 8000)            │
│                                                      │
│  - Auth & User management                           │
│  - Paper search & aggregation                       │
│  - Collection & notes management                    │
│  - AI feature orchestration                         │
│  - Bibliography generator                           │
└──────┬───────────┬──────────────────────────────────┘
       │           │
┌──────▼──────┐  ┌─▼──────────────────────────────────┐
│ PostgreSQL  │  │  External APIs                      │
│ (Port 5432) │  │                                     │
└──────┬──────┘  │  ┌─────────────────────────────┐   │
       │         │  │ Semantic Scholar API (gratis)│   │
┌──────▼──────┐  │  └─────────────────────────────┘   │
│   Redis     │  │  ┌─────────────────────────────┐   │
│   Cache     │  │  │ arXiv API (gratis)           │   │
│ (Port 6379) │  │  └─────────────────────────────┘   │
└─────────────┘  │  ┌─────────────────────────────┐   │
                 │  │ CrossRef API (gratis)         │   │
                 │  └─────────────────────────────┘   │
                 │  ┌─────────────────────────────┐   │
                 │  │ Groq API (gratis)            │   │
                 │  └─────────────────────────────┘   │
                 └────────────────────────────────────┘
```

---

## 5. Struktur Database (ERD)

### Tabel `users`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| name | string | Nama lengkap |
| email | string | Email unik |
| password | string | Hashed (bcrypt) |
| institution | string | Nama universitas/sekolah |
| research_interests | text | Minat riset (untuk suggestion) |
| created_at | timestamp | — |

### Tabel `papers` *(cache dari external API)*
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| external_id | string | ID dari Semantic Scholar / arXiv |
| source | enum | semantic_scholar / arxiv |
| title | string | Judul paper |
| authors | jsonb | Array nama author |
| abstract | text | Abstrak asli |
| year | integer | Tahun publikasi |
| doi | string | DOI (jika ada) |
| url | string | Link ke paper |
| citation_count | integer | Jumlah sitasi |
| fields_of_study | jsonb | Bidang ilmu |
| cached_at | timestamp | Waktu di-cache |

### Tabel `ai_summaries` *(cache hasil AI)*
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| paper_id | UUID | Foreign key → papers |
| summary_id | text | Ringkasan bahasa Indonesia |
| key_findings | jsonb | Poin-poin temuan utama |
| methodology | text | Metodologi singkat |
| generated_at | timestamp | Waktu generate |

### Tabel `collections`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Foreign key → users |
| name | string | Nama koleksi/folder |
| description | text | Deskripsi koleksi |
| is_public | boolean | Bisa dilihat orang lain |
| created_at | timestamp | — |

### Tabel `collection_papers`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| collection_id | UUID | Foreign key → collections |
| paper_id | UUID | Foreign key → papers |
| notes | text | Catatan pribadi untuk paper ini |
| highlights | jsonb | Highlight teks dari abstrak |
| added_at | timestamp | — |

### Tabel `search_history`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Foreign key → users |
| query | string | Query pencarian |
| filters | jsonb | Filter yang digunakan |
| result_count | integer | Jumlah hasil |
| searched_at | timestamp | — |

---

## 6. API Endpoints

### Auth
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
PUT    /api/auth/profile
```

### Paper Search
```
GET    /api/papers/search?q=&source=&year_from=&year_to=&field=
GET    /api/papers/{id}
GET    /api/papers/{id}/related
```

### Collections
```
GET    /api/collections
POST   /api/collections
PUT    /api/collections/{id}
DELETE /api/collections/{id}
POST   /api/collections/{id}/papers
DELETE /api/collections/{id}/papers/{paper_id}
PUT    /api/collections/{id}/papers/{paper_id}/notes
```

### Bibliography
```
POST   /api/bibliography/generate
       body: { paper_ids: [...], format: "APA" | "IEEE" | "Chicago" }
```

### AI Features
```
POST   /api/ai/summarize
       body: { paper_id }

POST   /api/ai/explain
       body: { text, language: "id" | "en" }

POST   /api/ai/gap-analysis
       body: { paper_ids: [...] }

POST   /api/ai/suggest-related
       body: { paper_id }
```

### Search History
```
GET    /api/history
DELETE /api/history/{id}
DELETE /api/history
```

---

## 7. Struktur Folder

### Backend (FastAPI / Python)
```
app/
├── main.py                         ← entry point FastAPI
├── core/
│   ├── config.py                   ← env variables & settings
│   ├── database.py                 ← PostgreSQL connection
│   ├── security.py                 ← JWT auth logic
│   └── cache.py                    ← Redis connection
├── routers/
│   ├── auth.py
│   ├── papers.py
│   ├── collections.py
│   ├── bibliography.py
│   ├── history.py
│   └── ai.py
├── models/
│   ├── user.py                     ← SQLAlchemy models
│   ├── paper.py
│   ├── collection.py
│   └── search_history.py
├── schemas/
│   ├── user.py                     ← Pydantic schemas
│   ├── paper.py
│   ├── collection.py
│   └── ai.py
├── services/
│   ├── semantic_scholar.py         ← wrapper Semantic Scholar API
│   ├── arxiv.py                    ← wrapper arXiv API
│   ├── crossref.py                 ← wrapper CrossRef API
│   ├── bibliography.py             ← logic format APA/IEEE/Chicago
│   └── groq.py                     ← wrapper Groq API
└── migrations/                     ← Alembic migrations
```

### Frontend (Vue.js 3)
```
src/
├── components/
│   ├── ui/                         ← komponen reusable
│   ├── papers/
│   │   ├── PaperCard.vue
│   │   ├── PaperDetail.vue
│   │   └── PaperSearchBar.vue
│   ├── collections/
│   │   ├── CollectionCard.vue
│   │   └── CollectionManager.vue
│   └── ai/
│       ├── SummaryPanel.vue
│       ├── GapAnalysisResult.vue
│       └── ExplainerChat.vue
├── views/
│   ├── auth/
│   │   ├── Login.vue
│   │   └── Register.vue
│   ├── Search.vue
│   ├── PaperDetail.vue
│   ├── Collections.vue
│   ├── CollectionDetail.vue
│   ├── GapAnalysis.vue
│   └── History.vue
├── stores/
│   ├── auth.js
│   ├── papers.js
│   ├── collections.js
│   └── ai.js
├── services/
│   └── api.js                      ← Axios instance
└── router/
    └── index.js
```

---

## 8. Docker Compose Setup

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/researchdb
      REDIS_URL: redis://redis:6379
      GROQ_API_KEY: ${GROQ_API_KEY}
      SEMANTIC_SCHOLAR_API_KEY: ${SEMANTIC_SCHOLAR_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: researchdb
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

---

## 9. Caching Strategy

Karena platform ini sangat bergantung pada external API, caching sangat penting untuk:
- Mengurangi jumlah request ke Semantic Scholar / arXiv
- Mempercepat response time
- Menghindari rate limiting

| Data | Cache di | TTL |
|---|---|---|
| Hasil search query | Redis | 1 jam |
| Metadata paper | PostgreSQL (tabel papers) | Permanen |
| AI Summary | PostgreSQL (tabel ai_summaries) | Permanen |
| Groq API response | Redis | 24 jam |
| Related paper suggestion | Redis | 6 jam |

---

## 10. Alur Kerja AI — Detail

### 10.1 Paper Summarizer Flow
```
User klik "Summarize" pada paper
        ↓
Cek tabel ai_summaries → sudah ada? Return cached result
        ↓ (belum ada)
Ambil abstrak paper dari tabel papers
        ↓
Kirim ke Groq API dengan prompt:
  "Ringkas paper berikut dalam bahasa Indonesia, 
   sertakan: ringkasan singkat, temuan utama, metodologi"
        ↓
Parse response → simpan ke tabel ai_summaries
        ↓
Return ke frontend → tampilkan di SummaryPanel
```

### 10.2 Research Gap Analyzer Flow
```
User pilih 3–10 paper dari koleksinya
        ↓
Frontend kirim array paper_ids ke /api/ai/gap-analysis
        ↓
Backend ambil abstrak semua paper yang dipilih
        ↓
Kirim ke Groq API (Gemma 2 9B) dengan prompt:
  "Dari paper-paper berikut, identifikasi:
   1. Topik yang sudah banyak diteliti
   2. Metodologi yang dominan digunakan
   3. Celah penelitian yang belum dieksplorasi
   4. Saran topik riset lanjutan"
        ↓
Return structured response → tampilkan sebagai GapAnalysisResult
```

### 10.3 Related Paper Suggester Flow
```
User klik "Find Related Papers" pada paper tertentu
        ↓
Backend ambil abstrak paper dari database
        ↓
Groq API ekstrak 5–8 keyword kunci dari abstrak
        ↓
Query keyword ke Semantic Scholar API
        ↓
Filter: exclude paper yang sudah ada di koleksi user
        ↓
Return 5–10 paper relevan yang belum diketahui user
```

---

## 11. Milestone & Timeline

| Minggu | Target |
|---|---|
| **1** | Setup project: FastAPI + Vue 3 + Docker Compose berjalan |
| **2** | Autentikasi selesai (register, login, JWT) |
| **3** | Integrasi Semantic Scholar API + arXiv API, search berfungsi |
| **4** | Collections & notes management selesai |
| **5** | AI Summarizer + Plain Language Explainer (Groq API) |
| **6** | Research Gap Analyzer + Related Paper Suggester |
| **7** | Bibliography generator (APA / IEEE / Chicago) |
| **8** | Polish UI, caching strategy, testing, deploy ke homelab |

---

## 12. Catatan Tambahan

- **Desain UI/UX:** Ditangani terpisah oleh developer (Figma/konsep sendiri)
- **Semantic Scholar API Key:** Daftar gratis di semanticscholar.org/product/api — naikkan rate limit dari 100 req/5 menit menjadi lebih tinggi
- **Groq API Key:** Daftar gratis di console.groq.com — tidak perlu kartu kredit
- **Backend pilihan FastAPI bukan Laravel:** Karena seluruh stack Python (Groq, httpx, SQLAlchemy) lebih kohesif dalam satu service tanpa microservice tambahan — lebih sederhana untuk project ini
- **AI summary di-cache:** Supaya tidak memanggil Groq API berulang kali untuk paper yang sama, hemat kuota gratis
- **Potensi pengembangan:** Bisa ditambahkan fitur upload PDF (PyMuPDF sudah familiar) untuk summarize paper yang tidak tersedia di Semantic Scholar/arXiv

---

*Brief ini bersifat living document — dapat diperbarui seiring perkembangan project.*

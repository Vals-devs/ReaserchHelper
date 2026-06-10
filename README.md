# ResearchFinder

**Platform riset akademik berbasis AI** yang membantu mahasiswa Indonesia menemukan, memahami, dan mengelola paper ilmiah dengan lebih efisien.

![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vuedotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38B2AC?logo=tailwind-css&logoColor=white)

---

## Daftar Isi

- [Tentang](#tentang)
- [Fitur Utama](#fitur-utama)
- [Tech Stack](#tech-stack)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Struktur Project](#struktur-project)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Docker Deployment](#docker-deployment)
- [Kontribusi](#kontribusi)

---

## Tentang

ResearchFinder dibangun untuk menyelesaikan masalah umum yang dihadapi mahasiswa saat mengerjakan skripsi atau tugas akhir:

- **Susah menemukan paper relevan** → Pencarian multi-sumber (Semantic Scholar + arXiv)
- **Abstrak bahasa Inggris sulit dipahami** → AI Summarizer + Terjemahan otomatis ke Bahasa Indonesia
- **Bingung menentukan research gap** → Research Gap Analyzer berbasis AI
- **Paper berantakan tidak terorganisir** → Koleksi + catatan per paper

---

## Fitur Utama

### 🔍 Pencarian Multi-Sumber
Cari paper dari **Semantic Scholar** dan **arXiv** secara bersamaan dalam satu query. Dilengkapi filter bidang studi, tahun, dan pengurutan berdasarkan sitasi.

### 🤖 AI Paper Summarizer
Ringkasan otomatis paper dalam **bahasa Indonesia** menggunakan Groq AI. Termasuk:
- Ringkasan 3-5 kalimat
- Temuan utama (key findings)
- Metodologi yang digunakan

### 💡 Research Gap Analyzer
Pilih 3-10 paper dari koleksi atau upload, lalu AI akan menganalisis:
- Topik yang sudah banyak diteliti
- Metodologi yang dominan
- **Celah penelitian** yang belum dieksplorasi
- Saran topik riset lanjutan

### 📄 Upload PDF + AI Extract
Upload paper PDF yang kamu download sendiri. AI otomatis extract:
- Judul, penulis, tahun
- Abstrak/ringkasan
- Full text untuk analisis

### 🌐 Terjemahan Abstrak
Terjemahkan abstrak bahasa Inggris ke **bahasa Indonesia** dengan satu klik. Istilah teknis tetap dipertahankan.

### 📚 Koleksi & Catatan
- Simpan paper ke koleksi terorganisir (folder)
- Tambahkan catatan pribadi per paper
- Sempurna untuk menyusun bab 2 skripsi

### 🔗 Paper Terkait
Temukan paper yang relevan berdasarkan rekomendasi Semantic Scholar atau pencarian berbasis keyword AI.

### 🕐 Riwayat Pencarian
Semua pencarian tersimpan otomatis. Klik "Cari Lagi" untuk mengulang pencarian sebelumnya.

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| **Frontend** | Vue 3, TypeScript, Vite, Tailwind CSS v4, Pinia, Vue Router |
| **Backend** | FastAPI (Python 3.10+), SQLAlchemy, Pydantic |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **Cache** | Redis |
| **AI** | Groq API (LLaMA 3.1 8B + LLaMA 3.3 70B) |
| **Paper API** | Semantic Scholar, arXiv |
| **PDF** | PyMuPDF |
| **Deployment** | Docker Compose, Nginx |

---

## Instalasi

### Prasyarat

- **Python** 3.10+
- **Node.js** 20+
- **Groq API Key** — Daftar gratis di [console.groq.com](https://console.groq.com)
- **Semantic Scholar API Key** — Daftar gratis di [semanticscholar.org](https://www.semanticscholar.org/product/api#api-key-form)

### 1. Clone Repository

```bash
git clone <repository-url>
cd ReaserchHelper
```

### 2. Setup Backend

```bash
cd backend

# Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Buat file .env
cp .env.example .env
```

Edit `backend/.env` dan isi API key:
```env
SECRET_KEY=ganti-dengan-random-string
DATABASE_URL=sqlite+aiosqlite:///./researchfinder.db
GROQ_API_KEY=gsk_xxxxx
SEMANTIC_SCHOLAR_API_KEY=s2k-xxxxx
```

Jalankan backend:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend akan berjalan di **http://localhost:8000**
API docs (Swagger): **http://localhost:8000/api/docs**

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Jalankan dev server
npm run dev
```

Frontend akan berjalan di **http://localhost:5173**

---

## Cara Penggunaan

### 1. Daftar Akun
Buka http://localhost:5173 dan klik **"Mulai Gratis"**. Isi nama, email, password, dan institusi.

### 2. Cari Paper
- Klik **"Search Papers"** di sidebar
- Ketik keyword (misal: "transformer attention mechanism")
- Filter berdasarkan sumber (Semantic Scholar / arXiv) dan bidang studi
- Klik paper untuk melihat detail

### 3. Pahami Paper dengan AI
Di halaman detail paper:
- **AI Summarize** → Ringkasan otomatis dalam bahasa Indonesia
- **Terjemahkan ke Indonesia** → Terjemahkan abstrak
- **Jelaskan Teks** → Paste bagian yang sulit, AI jelaskan dengan bahasa sederhana
- **Find Related** → Temukan paper terkait

### 4. Simpan ke Koleksi
- Klik **"Simpan ke Koleksi"** di halaman detail paper
- Pilih koleksi yang ada atau buat koleksi baru

### 5. Upload PDF
- Klik **"Gap Analysis"** → tab **"Upload PDF"**
- Drag & drop file PDF
- AI akan otomatis extract metadata (judul, penulis, abstrak)

### 6. Analisis Research Gap
- Klik **"Gap Analysis"** → tab **"Pilih Paper"**
- Filter sumber: Semua / Uploaded / Koleksi tertentu
- Pilih minimal 3 paper (maksimal 10)
- Klik **"Analisis Research Gap"**
- AI akan menampilkan: topik dominan, metodologi, celah penelitian, dan saran topik

### 7. Kelola Koleksi
- Klik **"Collections"** di sidebar
- Buka koleksi untuk melihat semua paper di dalamnya
- Tambahkan catatan per paper
- Hapus paper dari koleksi jika tidak relevan

---

## Struktur Project

```
ReaserchHelper/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── core/              # Config, database, security, cache
│   │   ├── routers/           # API endpoints (auth, papers, collections, ai, upload, history)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # External API wrappers (Groq, S2, arXiv, PDF)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                   # Environment variables
│
├── frontend/                   # Vue 3 Frontend
│   ├── src/
│   │   ├── App.vue            # Root component + sidebar layout
│   │   ├── router/            # Vue Router (10 routes)
│   │   ├── stores/            # Pinia stores (auth, papers, collections, ai, upload)
│   │   ├── services/          # Axios API client
│   │   ├── components/        # Reusable components
│   │   └── views/             # Page views (Landing, Dashboard, Search, etc.)
│   ├── vite.config.ts
│   └── package.json
│
├── designs/                    # UI mockup files (Canvas format)
├── docker-compose.yml          # Docker orchestration
├── nginx.conf                  # Reverse proxy config
└── checkpoint.md               # Development progress log
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register` | Daftar akun baru |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Profil user saat ini |
| PUT | `/api/auth/profile` | Update profil |

### Papers
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/papers/search?q=` | Cari paper (S2 + arXiv) |
| GET | `/api/papers/{id}` | Detail paper |
| GET | `/api/papers/{id}/related` | Paper terkait |

### Collections
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/collections/` | List semua koleksi |
| POST | `/api/collections/` | Buat koleksi baru |
| GET | `/api/collections/{id}` | Detail koleksi + papers |
| POST | `/api/collections/{id}/papers` | Tambah paper ke koleksi |
| DELETE | `/api/collections/{id}/papers/{pid}` | Hapus paper dari koleksi |

### AI Features
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/ai/summarize` | Ringkasan paper |
| POST | `/api/ai/translate` | Terjemahkan teks |
| POST | `/api/ai/explain` | Jelaskan teks |
| POST | `/api/ai/gap-analysis` | Analisis research gap |

### Upload
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/upload/pdf` | Upload PDF paper |
| GET | `/api/upload/papers` | List uploaded papers |
| DELETE | `/api/upload/{id}` | Hapus uploaded paper |

### History
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/history/` | Riwayat pencarian |
| DELETE | `/api/history/{id}` | Hapus riwayat |
| DELETE | `/api/history/` | Hapus semua riwayat |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `SECRET_KEY` | — | Secret key untuk JWT token |
| `DATABASE_URL` | `sqlite+aiosqlite:///./researchfinder.db` | Koneksi database |
| `GROQ_API_KEY` | — | API key dari console.groq.com |
| `SEMANTIC_SCHOLAR_API_KEY` | — | API key dari semanticscholar.org |
| `REDIS_URL` | — | Koneksi Redis (opsional untuk dev) |
| `REDIS_ENABLED` | `false` | Aktifkan Redis caching |

### Root (`.env` — untuk Docker)

Sama seperti backend, ditambah:
| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `POSTGRES_USER` | `postgres` | Username PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres` | Password PostgreSQL |
| `POSTGRES_DB` | `researchdb` | Nama database |

---

## Docker Deployment

Untuk deployment production menggunakan Docker:

```bash
# Pastikan .env di root sudah terisi
docker compose up -d --build
```

Service yang akan berjalan:
- **Nginx** (port 80) — Reverse proxy
- **Frontend** — Vue build statis
- **Backend** (port 8000) — FastAPI + Uvicorn
- **PostgreSQL** (port 5432) — Database
- **Redis** (port 6379) — Cache

Akses aplikasi di **http://localhost**

---

## Kontribusi

Project ini dibangun sebagai portofolio dan tool untuk mahasiswa Indonesia.

### Development Workflow
1. Backend: `uvicorn app.main:app --reload` (auto-reload saat file berubah)
2. Frontend: `npm run dev` (HMR aktif)
3. Database: SQLite auto-create tables saat startup

### Testing
```bash
# Test API via Swagger UI
open http://localhost:8000/api/docs

# Build check
cd frontend && npx vite build --mode development
```

---

## Lisensi

Project ini dibuat untuk keperluan akademik dan portofolio.

---

**Dibuat dengan ❤️ untuk mahasiswa Indonesia**

# DastoorAI

**An AI-Powered RAG Assistant for the Constitution of Pakistan**

DastoorAI is a production-deployed, multi-statute Legal Intelligence and Retrieval-Augmented Generation (RAG) platform covering the **Constitution of the Islamic Republic of Pakistan (1973)** and the **Pakistan Penal Code (Act XLV of 1860 — PPC)**. Built on a decoupled 3-tier cloud architecture, it combines **Hybrid Retrieval (Dense HNSW + Sparse BM25 with Reciprocal Rank Fusion)**, **FastEmbed ONNX embeddings**, **Groq LPU inference**, and **strict anti-hallucination guardrails** to deliver grounded, verifiable legal answers with exact statutory citations.

---

## Key Highlights

- **Multi-Statute Coverage (818 Provisions • 2,837 Chunks)**
  - **Constitution of Pakistan (1973):** `250` Articles • `911` discrete clauses
  - **Pakistan Penal Code (1860):** `568` Sections • `1,926` discrete chunks
- **Hybrid Retrieval + Reranking:** Combines `pgvector` HNSW semantic search (384-dimensional `all-MiniLM-L6-v2` vectors) with Sparse BM25 full-text search via Reciprocal Rank Fusion (`top_k=20`), refined by `FlashRankReranker` (`top_n=5`) and parent Article/Section context stitching.
- **Ultra-Lightweight Embedding Runtime:** Uses Qdrant's **FastEmbed** ONNX runtime (~50 MB RAM footprint) instead of heavy PyTorch/CUDA dependencies, enabling reliable execution within a 512 MB cloud container limit.
- **Anti-Hallucination & Prompt Injection Guardrails:**
  - Enforces strict citation discipline (`[Article X, Clause (Y)]`, `[PPC Section Z]`).
  - Maps colloquial user terms (e.g., *"firing"*) to formal statutory language (e.g., *PPC Section 337H / 286*) without fabricating provisions.
  - Explicitly refuses unsupported or fabricated laws (e.g., *"Article 999"*) and treats retrieved/user text as passive data against prompt injection.
- **Conversational Simplification & Multilingual Support:** Supports multi-turn follow-up condensation, plain-language simplification (*"explain in easy words"*), and **Urdu / Roman Urdu** responses while preserving official English statutory citations.
- **Sub-Millisecond Query Caching:** In-memory TTL cache returns repeated single-turn queries in `< 1 ms` (`~0.11–0.27 ms`), while cold retrieval + Groq LPU inference completes in `~1.5–4.9 s`.
- **Full Observability & Audit Trail:** Logs every request, route taken, cache status, latency breakdown (Total / Retrieval / Inference), token counts, citations, and user feedback into PostgreSQL.

---

## System Architecture

```text
                       WORLDWIDE USERS
                              │
                              ▼
         STREAMLIT COMMUNITY CLOUD (Frontend UI)
        frontend/app.py  •  Research Workspace UI
                              │
                              │  HTTPS REST (/api/v1)
                              ▼
             RENDER.COM (FastAPI API Gateway)
      app/main.py  •  FastEmbed ONNX  •  Hybrid RRF
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
     NEON CLOUD DATABASE              GROQ INFERENCE LPU
  PostgreSQL 18 + pgvector         openai/gpt-oss-120b
  (818 Provisions • 2,837 Chunks)  (Grounded Generation)
```

---

## Verified Evaluation & Performance Metrics

| Metric | Result | Notes |
|---|---|---|
| **Citation Accuracy** | `85.7%` | Automated evaluation suite |
| **Faithfulness (Anti-Hallucination)** | `91.4%` | Evaluated via `llm_judge.py` |
| **Automated Test Suite** | `10 / 10 Passing` | Pytest verification |
| **Cold Query Latency** | `~1.5 – 4.9 s` | Hybrid pgvector + BM25 + Groq LPU |
| **Cached Query Latency** | `0.11 – 0.27 ms` | In-memory TTL query cache |
| **Container Memory Footprint** | `~80 MB` | FastEmbed ONNX CPU runtime |

---

## Tech Stack

- **Frontend:** Streamlit (`frontend/app.py`) — *Research & Consultation*, *Statutory Codex*, *Observability & Telemetry*, and *Recent Consultations* session sidebar
- **Backend API:** FastAPI, Uvicorn, Pydantic v2 (`app/main.py`)
- **Database & Vector Search:** Neon Managed PostgreSQL 18, SQLAlchemy 2.0, `psycopg2-binary`, `pgvector` (HNSW + Full-Text Search)
- **Embeddings:** `fastembed` (`sentence-transformers/all-MiniLM-L6-v2`, 384-d)
- **LLM Inference:** `groq` (`openai/gpt-oss-120b`)
- **Hosting:** Neon (Database), Render (FastAPI Backend), Streamlit Community Cloud (Frontend)

---

## Project Structure

```text
DastoorAI/
├── app/
│   ├── main.py                         # FastAPI application entrypoint
│   ├── core/
│   │   └── config.py                   # Typed Pydantic settings & Neon SSL config
│   ├── api/
│   │   └── v1/
│   │       ├── router.py               # Central v1 API router
│   │       └── endpoints/
│   │           ├── health.py           # Service health checks
│   │           ├── query.py            # Main RAG query endpoint
│   │           ├── articles.py         # Statutory lookup / Codex endpoints
│   │           ├── sessions.py         # Consultation history endpoints
│   │           ├── feedback.py         # User feedback audit endpoint
│   │           └── analytics.py        # Observability & telemetry endpoints
│   ├── cache/
│   │   ├── key_builder.py              # Deterministic query cache keys
│   │   └── redis_client.py             # In-memory TTL cache manager
│   ├── db/
│   │   ├── session.py                  # SQLAlchemy SessionLocal & engine
│   │   └── models/
│   │       └── audit.py                # QueryLog & FeedbackLog ORM models
│   ├── rag/
│   │   ├── embeddings/
│   │   │   └── sentence_transformer.py # FastEmbed ONNX 384-d provider
│   │   ├── ingestion/
│   │   │   └── parser.py               # Legal parser with footnote & Part scoping
│   │   ├── retrieval/
│   │   │   ├── hybrid.py               # Dense HNSW + Sparse BM25 + RRF retriever
│   │   │   └── parent_stitcher.py      # Parent Article/Section context stitching
│   │   ├── reranking/
│   │   │   └── cross_encoder.py        # FlashRankReranker (top_n=5)
│   │   ├── routing/
│   │   │   └── query_router.py         # Domain scope router (HYBRID_RAG / OUT_OF_SCOPE)
│   │   ├── generation/
│   │   │   ├── engine.py               # Multi-statute RAG orchestrator
│   │   │   ├── prompts.py              # System prompts, condensation & guardrails
│   │   │   └── groq_provider.py        # Groq API client wrapper
│   │   └── evaluation/
│   │       ├── llm_judge.py            # Faithfulness LLM-as-a-Judge evaluator
│   │       └── retrieval_metrics.py    # MRR & retrieval metrics
│   └── schemas/
│       ├── article.py                  # Feedback & article Pydantic schemas
│       └── query.py                    # Query request/response schemas
├── frontend/
│   └── app.py                          # Streamlit Legal Intelligence Platform UI
├── scripts/
│   ├── ingest_constitution.py          # Ingests 250 Constitution articles (911 chunks)
│   └── ingest_ppc.py                   # Ingests 568 PPC sections (1,926 chunks)
├── requirements.txt                    # Production Python dependencies
└── .env                                # Local environment variables (gitignored)
```

---

## Database Schema Overview

Hosted on **Neon Cloud PostgreSQL 18** with `uuid-ossp` and `vector` (`pgvector`) extensions enabled:

- `document_versions` — Tracks ingested statutes and versions (`law_type`: `CONSTITUTION` / `PPC`)
- `articles` — Stores parent Articles/Sections, titles, parts/chapters, and `law_type`
- `clauses` — Stores discrete clauses/chunks linked to parent articles
- `embeddings` — Stores 384-dimensional `pgvector` embeddings with HNSW indexing
- `query_logs` — Stores audit telemetry (`request_id`, `route_taken`, `retrieval_strategy`, `cache_hit`, latency breakdown, token usage, `cited_articles`)
- `feedback_logs` — Stores user ratings (`+1` / `-1`), reason categories, and notes

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jagdesh666/DastoorAI.git
cd DastoorAI
```

### 2. Create a Virtual Environment & Install Dependencies

Requires **Python 3.11** (recommended for full compatibility across cloud & local runtimes):

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```ini
DB_HOST=your-neon-pooler-host.aws.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_neon_password

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

# Optional for frontend (defaults to live backend if configured)
API_BASE_URL=http://127.0.0.1:8000/api/v1
```

> **Note:** Neon strictly requires `sslmode=require`, which is automatically enforced in `app/core/config.py`.

### 4. Prepare Database & Ingest Legal Corpus

Ensure `law_type` columns exist in your Neon/PostgreSQL schema:

```sql
ALTER TABLE document_versions ADD COLUMN IF NOT EXISTS law_type VARCHAR(50) DEFAULT 'CONSTITUTION';
ALTER TABLE articles ADD COLUMN IF NOT EXISTS law_type VARCHAR(50) DEFAULT 'CONSTITUTION';
```

Run both ingestion scripts to parse, chunk, embed, and store all 818 provisions:

```bash
python scripts/ingest_constitution.py
python scripts/ingest_ppc.py
```

> **Windows Hugging Face Cache Tip:** If you encounter an `Access is denied (os error 5)` error from `hf_xet` during model download on Windows, set temporary cache paths in Command Prompt before running ingestion:
> ```bat
> set HF_HUB_DISABLE_XET=1
> set HF_HOME=%TEMP%\hf_cache
> set HF_HUB_CACHE=%TEMP%\hf_cache\hub
> set FASTEMBED_CACHE_PATH=%TEMP%\fastembed_cache
> python scripts/ingest_ppc.py
> ```

Verify ingested counts in PostgreSQL:

```sql
SELECT law_type, COUNT(*) FROM articles GROUP BY law_type;
-- Expected: CONSTITUTION = 250, PPC = 568
```

### 5. Run Locally

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, launch the Streamlit frontend:

```bash
streamlit run frontend/app.py
```

- **Frontend UI:** `http://localhost:8501`
- **Swagger API Docs:** `http://127.0.0.1:8000/docs`

---

## API Reference (`/api/v1`)

All endpoints are mounted under `/api/v1` in `app/api/v1/router.py`:

| Group | Purpose |
|---|---|
| `Health` | Backend & database connectivity status |
| `RAG Queries` | Executes hybrid retrieval, reranking, Groq generation, caching, and logging |
| `Articles` | Direct statutory lookup for the *Statutory Codex* |
| `Sessions` | Lists and retrieves historical consultation sessions |
| `Feedback` | Records user feedback against `request_id` in `feedback_logs` |
| `Analytics & Observability` | Serves query latency, cache hit rates, and audit telemetry |

Interactive OpenAPI documentation is available at `https://<your-render-service>.onrender.com/docs`.

---

## Cloud Deployment Guide

### 1. Database — Neon
- Provision a PostgreSQL database on [Neon](https://neon.tech) with `pgvector` enabled.
- Use the **pooler endpoint** (`-pooler...aws.neon.tech`) in your environment variables.

### 2. Backend API — Render.com
1. Create a new **Web Service** linked to your GitHub repository.
2. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `PYTHON_VERSION` = `3.11.9`
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - `GROQ_API_KEY`, `GROQ_MODEL`

### 3. Frontend UI — Streamlit Community Cloud
1. Deploy `frontend/app.py` on [Streamlit Community Cloud](https://share.streamlit.io).
2. In **App Settings → Secrets**, configure your Render backend URL (ensure `/api/v1` is appended):
   ```toml
   API_BASE_URL = "https://<your-render-service>.onrender.com/api/v1"
   ```

---

## Legal Disclaimer

*This platform is provided strictly for educational, research, and general informational purposes. It is not a substitute for certified legal counsel and does not constitute formal legal advice. For specific legal matters, always consult a qualified advocate or attorney licensed in Pakistan.*

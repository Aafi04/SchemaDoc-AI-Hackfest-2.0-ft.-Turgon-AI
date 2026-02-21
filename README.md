<div align="center">

# SchemaDoc AI

### Intelligent Data Dictionary Agent

_Hackfest 2.0 ft. Turgon AI — Team Dual Core_

Mohd Aafi (Team Lead) · Rahul Kumar (Frontend Developer)

[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI_Engine-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)

</div>

---

## Overview

SchemaDoc AI connects to **any SQL database** — SQLite, PostgreSQL, MySQL, or MSSQL — and automatically generates a complete, AI-enriched data dictionary with quality scoring, relationship visualization, natural language querying, and business-ready reports.

The system uses a **cyclic LangGraph state machine** with a deterministic validation gate that catches AI hallucinations, prevents data loss, and self-corrects via retry loops — guaranteeing schema integrity.

---

## Architecture

```
┌──────────────┐      ┌─────────────────┐     ┌──────────────────┐      ┌──────────────┐
│   Extract    │────▶│  AI Enrichment  │────▶│   Validation     │────▶│   Dashboard  │
│  (SQLAlchemy)│      │  (Gemini + ReAct│     │   Gate           │      │  (Next.js)   │
│  + Profiling │      │   Tool-Calling) │     │  (Deterministic) │      │              │
└──────────────┘      └─────────────────┘     └───────┬──────────┘      └──────────────┘
                           ▲                          │
                           │    FAILED + retry < 3    │
                           └──────────────────────────┘
```

| Layer                 | Role                                                           | Technology                         |
| --------------------- | -------------------------------------------------------------- | ---------------------------------- |
| **Data Ingestion**    | Dialect-agnostic schema extraction + statistical profiling     | SQLAlchemy 2.0, ThreadPoolExecutor |
| **Orchestration**     | Cyclic state machine with conditional retry edges              | LangGraph                          |
| **Enrichment Engine** | Semantic analysis with forensic log evidence via ReAct agents  | Gemini 2.5 Flash + LangChain       |
| **Validation Gate**   | Anti-hallucination guard — column-level integrity verification | Deterministic Python               |
| **Backend API**       | REST API serving pipeline, chat, export, and schema endpoints  | FastAPI + Uvicorn                  |
| **Frontend**          | Interactive dashboard with 6 pages                             | Next.js 15 + TailwindCSS           |

---

## Features

| Page                 | Description                                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Dashboard**        | Run pipelines against demo or enterprise databases, animated pipeline visualizer with real-time stage tracking, retry visualization   |
| **Schema Explorer**  | Full table browser with per-column stats, tags (PK/FK/PII/UNIQUE), AI descriptions, sample values, null/unique percentages            |
| **Knowledge Graph**  | Interactive ER diagram — ReactFlow-powered node graph with foreign key edges and table metadata                                       |
| **NL → SQL Chat**    | Natural language to SQL interface grounded in enriched schema context, markdown-rendered responses with syntax-highlighted SQL        |
| **Business Reports** | AI-generated executive overview, domain detection, quality issues, relationship map, per-table documentation, downloadable as MD/JSON |

### Anti-Hallucination Pipeline

- **Deterministic Validation Gate** compares every AI-enriched column set against the raw source of truth
- Detects **data loss** (missing columns) and **hallucinations** (invented columns)
- Automatically retries enrichment up to 3 times on failure
- Full execution trace visible in the animated Pipeline Visualizer

### Performance

- **Batched SQL profiling** — all column stats computed in one query per table (not per-column)
- **Parallel table processing** — ThreadPoolExecutor profiles tables concurrently
- **Schema caching** — unchanged schemas skip AI enrichment entirely
- **Report caching** — business reports generated once per run, served instantly on revisit

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Google Gemini API key](https://aistudio.google.com/apikey)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Aafi04/SchemaDoc-AI-Hackfest-2.0-ft.-Turgon-AI.git
cd SchemaDoc-AI-Hackfest-2.0-ft.-Turgon-AI

# Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start the backend
uvicorn backend.main:app --reload --port 8001
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard opens at **http://localhost:3000**. The backend API runs at **http://localhost:8001**.

### Demo Databases

```bash
# Download Chinook (11 tables — music store)
python data/scripts/get_chinook.py

# Download Olist (8 tables — Brazilian e-commerce, 550k+ rows)
python data/scripts/get_olist.py

# Download Bike Store (9 tables — retail sales)
python data/scripts/get_bikestore.py

# Or generate the small 3-table demo database
python setup_demo.py
```

Select any database from the dashboard dropdown and click **Run Pipeline**.

---

## Project Structure

```
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── core/
│   │   ├── config.py               # Settings (Pydantic BaseSettings)
│   │   └── state.py                # TypedDict state definitions
│   ├── api/routes/
│   │   ├── pipeline.py             # Pipeline execution + database listing
│   │   ├── schema.py               # Schema overview + table detail
│   │   ├── chat.py                 # NL → SQL chat endpoint
│   │   └── export.py               # JSON/MD export + AI business reports
│   ├── connectors/
│   │   └── sql_connector.py        # SQLAlchemy extraction + batched profiling
│   ├── pipeline/
│   │   ├── graph.py                # LangGraph pipeline builder
│   │   └── nodes/
│   │       ├── enrichment_node.py  # Gemini ReAct enrichment
│   │       └── validation_node.py  # Anti-hallucination gate
│   └── services/
│       ├── pipeline_service.py     # Run management + execution
│       └── usage_search.py         # Forensic log search (ReAct tool)
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx                # Landing page
│   │   └── dashboard/
│   │       ├── page.tsx            # Pipeline runner + visualizer
│   │       ├── schema/page.tsx     # Schema explorer
│   │       ├── graph/page.tsx      # ER knowledge graph
│   │       ├── chat/page.tsx       # NL → SQL chat
│   │       └── reports/page.tsx    # Business report viewer
│   ├── src/components/
│   │   ├── PipelineVisualizer.tsx  # Animated pipeline stage component
│   │   └── layout/                 # NavRail, TopBar, AppShell
│   └── src/lib/
│       ├── api.ts                  # API client + TypeScript types
│       └── utils.ts                # Utility functions
├── shared/
│   └── schemas.py                  # Pydantic models shared across backend
├── data/
│   ├── scripts/                    # Database download scripts
│   └── usage_logs.sql              # Query logs for ReAct tool
└── src/                            # Original Streamlit prototype (legacy)
```

---

## Tech Stack

| Component              | Technology                              |
| ---------------------- | --------------------------------------- |
| AI Model               | Google Gemini 2.5 Flash                 |
| Orchestration          | LangGraph (cyclic StateGraph)           |
| LLM Framework          | LangChain Core + LangChain Google GenAI |
| Database Introspection | SQLAlchemy 2.0 (dialect-agnostic)       |
| Backend API            | FastAPI + Uvicorn                       |
| Frontend               | Next.js 15, TypeScript, TailwindCSS     |
| Animations             | Framer Motion                           |
| Data Fetching          | TanStack React Query                    |
| ER Visualization       | ReactFlow                               |
| Markdown Rendering     | react-markdown + remark-gfm             |

---

## Deployment

### Backend → Railway (Free Tier)

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Set **Root Directory** to `backend`
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add env var: `GOOGLE_API_KEY` = your key, `CORS_ORIGINS` = your Vercel URL

### Frontend → Vercel (Free Tier)

1. [vercel.com](https://vercel.com) → Add New Project → Import repo
2. Set **Root Directory** to `frontend`
3. Add env var: `NEXT_PUBLIC_API_URL` = your Railway backend URL

> API keys are set in each platform's dashboard — never committed to Git.

---

## Team Dual Core

Built for **Hackfest 2.0 ft. Turgon AI** — February 2026.

<div align="center">

# ⚡ SchemaDoc AI

### AI-Powered Data Dictionary Generator

_Hackfest 2.0 — Team Dual Core_

Mohd Aafi (Team Lead) mdaafi04@gmail.com || Rahul Kumar (Frontend Developer) rahulkumar108642@gmail.com

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI_Engine-4285F4?logo=google&logoColor=white)](https://ai.google.dev)

</div>

---

## Overview

SchemaDoc AI connects to any SQL database and automatically generates a complete, AI-enriched data dictionary with quality scoring, knowledge graphs, and natural language querying.

The system uses a **cyclic LangGraph state machine** with a deterministic validation gate that catches AI hallucinations, prevents data loss, and self-corrects via retry loops — guaranteeing schema integrity.

---

## Architecture

```
┌──────────────┐      ┌─────────────────┐     ┌──────────────────┐      ┌─────────────┐
│   Extract    │────▶│  AI Enrichment  │────▶│   Validation     │────▶│   Output    │
│  (SQLAlchemy)│      │  (Gemini + ReAct│     │   Gate           │      │  (Streamlit)│
│              │      │   Tool-Calling) │     │  (Deterministic) │      │             │
└──────────────┘      └─────────────────┘     └───────┬──────────┘      └─────────────┘
                           ▲                          │
                           │    FAILED + retry < 3    │
                           └──────────────────────────┘
```

| Layer                 | Role                                                           | Technology                   |
| --------------------- | -------------------------------------------------------------- | ---------------------------- |
| **Data Ingestion**    | Dialect-agnostic schema extraction + statistical profiling     | SQLAlchemy 2.0               |
| **Orchestration**     | Cyclic state machine with conditional retry edges              | LangGraph                    |
| **Enrichment Engine** | Semantic analysis with forensic log evidence via ReAct agents  | Gemini 2.5 Flash + LangChain |
| **Validation Gate**   | Anti-hallucination guard — column-level integrity verification | Deterministic Python         |
| **Presentation**      | Interactive dashboard with 4 tabs                              | Streamlit + streamlit-agraph |

---

## Features

| Tab                    | Description                                                                                                                                         |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **📊 Overview**        | KPI metrics, AI-generated database summary, health bars, quality alerts, and a full **Pipeline Integrity Log** showing retry/self-correction events |
| **📋 Schema Explorer** | Table selector with per-column expanders showing stats, tags (PK/FK/PII), descriptions, and sample values                                           |
| **🕸️ Knowledge Graph** | Interactive ER visualization — node size ∝ row count, color = health score, edges = foreign keys                                                    |
| **💬 NL → SQL**        | ChatGPT-style natural language to SQL interface grounded in the enriched schema context                                                             |

### Anti-Hallucination Pipeline

- **Deterministic Validation Gate** compares every AI-enriched column set against the raw source of truth
- Detects **data loss** (missing columns) and **hallucinations** (invented columns)
- Automatically retries enrichment up to 3 times on failure
- Full execution trace with caught violations visible in the Pipeline Integrity Log

---

## Quick Start

### Prerequisites

- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/apikey)

### Setup

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
```

### Download Demo Database

```bash
python data/scripts/get_chinook.py
```

This downloads the [Chinook](https://github.com/lerocha/chinook-database) sample database (11 tables — music store data).

Optionally, generate the smaller 3-table demo database:

```bash
python setup_demo.py
```

### Run

```bash
python run_app.py
```

Or directly:

```bash
streamlit run src/interface/app.py
```

The dashboard opens at **http://localhost:8501**. Select a database from the sidebar and click **⚡ Analyze Database**.

---

## Project Structure

```
├── .env.example            # Environment template (copy to .env)
├── .streamlit/
│   └── config.toml         # Streamlit dark theme config
├── requirements.txt
├── run_app.py              # Streamlit launcher
├── setup_demo.py           # Creates demo.db + mock usage logs
├── architecture-spec.html  # Detailed architecture specification
├── data/
│   ├── scripts/
│   │   └── get_chinook.py  # Downloads Chinook SQLite DB
│   └── usage_logs.sql      # Query logs for ReAct forensic tool
└── src/
    ├── core/
    │   ├── config.py       # App configuration (paths, API keys)
    │   └── state.py        # TypedDict state definitions (AgentState)
    ├── backend/
    │   ├── connectors/
    │   │   └── sql_connector.py   # SQLAlchemy schema extraction + profiling
    │   └── services/
    │       └── usage_search.py    # Forensic log search (ReAct tool)
    ├── pipeline/
    │   ├── graph.py               # LangGraph pipeline builder
    │   └── nodes/
    │       ├── enrichment_node.py # AI enrichment with Gemini + tool-calling
    │       └── validation_node.py # Deterministic anti-hallucination gate
    └── interface/
        └── app.py                 # Streamlit dashboard (979 lines)
```

---

## Tech Stack

| Component              | Technology                              |
| ---------------------- | --------------------------------------- |
| AI Model               | Google Gemini 2.5 Flash                 |
| Orchestration          | LangGraph (cyclic StateGraph)           |
| LLM Framework          | LangChain Core + LangChain Google GenAI |
| Database Introspection | SQLAlchemy 2.0 (dialect-agnostic)       |
| Frontend               | Streamlit 1.54 + streamlit-agraph       |
| Language               | Python 3.11                             |

---

## Team Dual Core

Built for **Hackfest 2.0 ft Turgon AI** — February 2026.

</div>

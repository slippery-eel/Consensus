# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Consensus is a full-stack survey analysis tool. Users create surveys, collect votes (agree/disagree/pass), then analyze results using PCA + K-means clustering with optional OpenAI-generated descriptions of each opinion group.

## Development Commands

**Backend** (FastAPI + SQLite, port 8000):
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend** (React + Vite, port 5173):
```bash
cd frontend
npm install
npm run dev       # dev server with HMR
npm run build     # tsc -b + vite build
npm run lint      # ESLint
```

**Seed data** (backend must be running):
```bash
python seed.py    # Creates "American Political Opinions" survey with 30 statements and 10 fake participants
```

Vite proxies `/api/*` to `http://localhost:8000`, so the frontend only needs the dev server running at `http://localhost:5173`.

## Architecture

### Backend (`backend/app/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app, CORS config, router registration |
| `database.py` | SQLite + SQLAlchemy setup (tables auto-created on startup) |
| `models.py` | ORM: Survey, Statement, Participant, Response, GroupSummary, Setting |
| `schemas.py` | Pydantic v2 validation schemas |
| `analytics.py` | PCA + K-means clustering pipeline |
| `summarizer.py` | OpenAI (gpt-4o-mini) integration for group descriptions |
| `routers/` | One file per resource group (surveys, statements, participants, responses, analysis, summaries, settings) |

All routes are prefixed with `/api`.

### Frontend (`frontend/src/`)

| Path | Purpose |
|------|---------|
| `App.tsx` | React Router: `/admin`, `/survey/:id`, `/results/:id`, `/results/:id/cluster/:clusterId` |
| `api.ts` | Axios client + all TypeScript interfaces for API data |
| `pages/Admin.tsx` | Survey management, statement editor, response table, API key settings |
| `pages/Survey.tsx` | Single-statement voter UI; sessions + votes persisted in localStorage |
| `pages/Results.tsx` | Analysis dashboard: k selector, scatter plot, statement stats, AI summaries |
| `pages/ClusterDetail.tsx` | Deep dive into a single cluster's AI-generated description |
| `components/` | ClusterPlot (Recharts scatter), StatementTable, GroupSummaryCard, ConsensusList, DivisiveList |

### Data Flow

1. **Admin** creates survey → adds statements
2. **Respondents** visit `/survey/:id` → session created (POST `/api/surveys/{id}/sessions`) → votes submitted (POST `/api/sessions/{id}/responses`)
3. **Results** page runs clustering (POST `/api/surveys/{id}/analyze?k=N`) → optionally generates AI summaries (POST `/api/surveys/{id}/summarize?k=N`)

### Analysis Pipeline (`analytics.py`)

1. Build vote matrix: participants × statements (agree=1, disagree=-1, pass=0)
2. Standardize, apply PCA (2 components for scatter plot)
3. K-means on PCA coordinates (random seed=42)
4. Compute per-statement stats: `is_consensus` (≥70% agree, ≤20% disagree), `is_divisive` (35–65% agree + disagree split), `cluster_score` (max variance between cluster means)

### AI Summaries (`summarizer.py`)

- Calls OpenAI gpt-4o-mini with a structured prompt per cluster (distinguishing statements, strong agree/disagree, cross-group consensus)
- Returns JSON: `label`, `description`, `core_beliefs`, `key_disagreement`
- Cached in `group_summaries` table; use `force=true` to regenerate

## Key Constraints

- **CORS**: Backend only allows `http://localhost:5173`
- **TypeScript strict**: `noUnusedLocals` and `noUnusedParameters` are enabled
- **OpenAI key**: Stored in the `settings` DB table; required for summary generation
- **No migrations**: SQLAlchemy creates all tables on startup from `models.py`
- **LocalStorage key**: `consensus_session_{surveyId}` stores the participant session and vote state

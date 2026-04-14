# Consensus

A full-stack survey analysis tool that identifies distinct opinion groups within a population. Create surveys, collect votes, then use machine learning and AI to discover and describe clusters of like-minded respondents.

## How It Works

1. **Create a survey** — add a set of statements on any topic
2. **Collect votes** — share the survey link; participants vote agree, disagree, or pass on each statement
3. **Analyze** — run PCA + K-means clustering to group participants by voting pattern
4. **Describe** — optionally generate AI summaries (via OpenAI) describing each group's beliefs and key disagreements

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Recharts, React Router |
| Backend | FastAPI, SQLAlchemy, SQLite |
| ML | scikit-learn (PCA + K-means) |
| AI | OpenAI gpt-4o-mini |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key (optional — only needed for AI group descriptions)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api` requests to the backend automatically.

### Seed Data (optional)

With the backend running, populate a sample "American Political Opinions" survey with 30 statements and 10 fake participants:

```bash
python seed.py
```

## Usage

### Admin (`/admin`)
- Create and manage surveys
- Add, edit, or deactivate statements
- View raw response data
- Configure your OpenAI API key (stored locally in the database)

### Survey (`/survey/:id`)
- Share this URL with participants
- Statements are presented one at a time; participants vote agree / disagree / pass
- Progress is saved in localStorage so the survey can be resumed

### Results (`/results/:id`)
- Choose the number of groups (k = 2–4) to cluster participants into
- View a 2D scatter plot of participants colored by cluster (PCA-reduced)
- See which statements drive the most consensus or division
- Generate AI-written descriptions of each group (requires OpenAI key)

## Analysis Details

Votes are encoded as a matrix (participants × statements) where agree = 1, disagree = −1, pass = 0. The pipeline:

1. Standardize the vote matrix
2. Reduce to 2 dimensions with PCA (used for the scatter plot)
3. Cluster participants with K-means (seed = 42 for reproducibility)
4. Score each statement by how well it distinguishes clusters

**Consensus** statements: ≥70% agree, ≤20% disagree  
**Divisive** statements: 35–65% split between agree and disagree

## Project Structure

```
Consensus/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── analytics.py     # PCA + K-means pipeline
│   │   ├── summarizer.py    # OpenAI integration
│   │   └── routers/         # API endpoints by resource
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/           # Admin, Survey, Results, ClusterDetail
│       ├── components/      # ClusterPlot, StatementTable, GroupSummaryCard, …
│       └── api.ts           # Typed Axios client
├── seed.py                  # Sample data generator
└── CLAUDE.md                # AI assistant guidance
```

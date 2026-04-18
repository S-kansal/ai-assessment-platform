# AI Engineering Assessment Platform

A simulation-based hiring assessment platform that evaluates AI engineers on real-world skills — RAG pipeline debugging, prompt engineering, and AI system failure diagnosis.

---

## Overview

Traditional coding interviews test algorithmic knowledge. This platform tests the work AI engineers actually do: debugging broken retrieval pipelines, fixing unstable prompts, and diagnosing why a system is hallucinating.

Candidates interact with deterministic AI system simulations. Their every action — prompt edits, retrieval inspections, simulation runs, written diagnoses — is captured as telemetry and scored across five dimensions.

---

## Architecture

```
Candidate Interface  →  Task Engine  →  Simulation Engine
                                    ↓
                         Telemetry Engine
                                    ↓
                         Evaluation Engine
                                    ↓
                          Scoring Engine
                                    ↓
                     Hiring Manager Dashboard
```

**Backend:** FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
**Frontend:** React + Vite + Tailwind CSS
**Auth:** JWT (HS256) with role-based access control
**Multi-tenancy:** All data scoped by `organization_id`

---

## Features

- **3 RAG debugging tasks** — irrelevant retrieval, bad chunking, context-ignored prompt
- **Deterministic simulations** — same input always produces same output; candidates are compared fairly
- **Telemetry capture** — every action logged with timestamps (simulation runs, prompt edits, retrieval inspections, solution submissions)
- **Rule-based evaluation** — diagnostic accuracy, task success, debugging efficiency, iteration quality
- **Capability scoring** — weighted composite score mapped to capability profile (RAG debugging, prompt engineering)
- **Hiring manager dashboard** — candidate scorecards, capability radar charts, session replay, task-level breakdowns
- **Pilot program flow** — public registration, assessment, post-assessment feedback survey

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # or create .env with DATABASE_URL and JWT_SECRET
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app is at `http://localhost:5173`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite:///./local.db` | SQLAlchemy connection string |
| `JWT_SECRET` | Yes | insecure default | Secret key for JWT signing |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Comma-separated allowed origins |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `SENTRY_DSN` | No | — | Sentry error tracking DSN |
| `REDIS_URL` | No | — | Redis URL for Celery (optional) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Backend API base URL |

---

## API Overview

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/org/register` | Register organization + admin user |
| `POST` | `/auth/login` | Login, returns JWT token |

### Assessment Flow (Candidate)

| Method | Path | Description |
|---|---|---|
| `POST` | `/assessments/start` | Start multi-task assessment |
| `POST` | `/assessments/{id}/advance` | Submit current task, advance to next |
| `GET` | `/assessments/{id}` | Get assessment status |
| `POST` | `/simulate/rag` | Run RAG simulation |
| `POST` | `/telemetry` | Log a candidate action |

### Dashboard (Hiring Manager — requires JWT)

| Method | Path | Description |
|---|---|---|
| `GET` | `/dashboard/candidates` | List org candidates (paginated) |
| `GET` | `/dashboard/candidates/{id}/profile` | Capability profile |
| `GET` | `/dashboard/candidates/{id}/tasks` | Task performance breakdown |
| `GET` | `/dashboard/task-runs/{id}/telemetry` | Session telemetry |
| `GET` | `/dashboard/task-runs/{id}/evaluation` | Evaluation scores |

### Pilot Program (Public)

| Method | Path | Description |
|---|---|---|
| `POST` | `/pilot/register` | Register pilot participant |
| `POST` | `/pilot/feedback` | Submit post-assessment feedback |
| `GET` | `/pilot/analytics` | Aggregate pilot stats |
| `GET` | `/pilot/report` | Full report (admin JWT required) |

---

## Assessment Flow

1. Candidate visits `/pilot` or `/assess`
2. Registers (or starts directly)
3. `POST /assessments/start` — creates session, starts task 1
4. Candidate runs simulations, edits prompts, inspects retrieval logs
5. Each action emits a telemetry event via `POST /telemetry`
6. Candidate submits diagnosis + fix via `POST /assessments/{id}/advance`
7. Platform evaluates task, starts task 2 (or completes assessment)
8. On completion: scoring runs, capability profile generated
9. Candidate optionally completes feedback survey
10. Hiring manager reviews candidate in dashboard

---

## Scoring Model

Scores are calculated per task then aggregated by capability:

| Dimension | Weight | Signal |
|---|---|---|
| Diagnostic Accuracy | 40% | Did the solution text match failure-mode keywords? |
| Task Success | 30% | Solution submitted + at least one simulation run |
| Efficiency | 20% | Fewer simulation runs = more targeted debugging |
| Iteration Quality | 10% | Inspected retrieval before editing; balanced edit/run ratio |

**Capability map:**

| Task | Capability |
|---|---|
| `rag_debug_01` | `rag_debugging` |
| `rag_debug_02` | `rag_debugging` |
| `rag_debug_03` | `prompt_engineering` |

---

## Deployment

### Backend — Render

The `render.yaml` at the repo root configures a web service:

```
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port 10000
Root:  backend/
```

Set `DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS` in the Render environment dashboard.

### Frontend — Vercel

Push to `main`. Vercel auto-deploys. The `frontend/vercel.json` proxies `/api/*` requests to the Render backend URL.

Set `VITE_API_BASE_URL` to your Render service URL in Vercel's environment settings, or leave it as `/api` to use the proxy rewrite.

### Docker

A `Dockerfile` in `backend/` builds the API image:

```bash
docker build -t ai-assessment-api ./backend
docker run -p 8000:8000 --env-file backend/.env ai-assessment-api
```

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── assessment/      # Multi-task orchestrator, routes
│   │   ├── auth/            # JWT, user models, tenant guard
│   │   ├── core/            # Logging, rate limiting, Celery config
│   │   ├── evaluation/      # Evaluator pipeline, rules, metrics
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── org/             # Organization (tenant) model
│   │   ├── pilot/           # Pilot program routes and models
│   │   ├── routes/          # API route handlers
│   │   ├── scoring/         # Score calculator, aggregator, capability map
│   │   ├── services/        # Telemetry service
│   │   ├── simulation/      # RAG simulator, failure modes, documents
│   │   └── tasks/           # Task runner, task definitions
│   ├── migrations/          # Alembic migration scripts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # Auth context
│   │   ├── pages/           # Route pages
│   │   └── services/        # API client
│   └── package.json
├── render.yaml
└── README.md
```

---

## Security Notes

- Passwords are hashed with bcrypt via passlib
- All API endpoints that return tenant data require a valid JWT
- Dashboard routes enforce `organization_id` scoping on every query
- The pilot report endpoint requires the `admin` role
- Rate limiting is applied to simulation endpoints (30 req/min per IP)
- Security headers (X-Content-Type-Options, X-Frame-Options, etc.) are added to all responses

# AI Engineering Assessment Platform

A multi-tenant SaaS platform for evaluating AI engineers through realistic debugging tasks — not coding puzzles.

Candidates are placed inside simulated RAG pipeline failures. They inspect logs, revise prompts, run simulations, and submit diagnoses. The platform records every action, evaluates reasoning quality deterministically, and produces a structured capability profile for hiring teams.

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Usage Walkthrough](#usage-walkthrough)
- [API Reference](#api-reference)
- [Assessment Lifecycle](#assessment-lifecycle)
- [Evaluation and Scoring](#evaluation-and-scoring)
- [Deployment](#deployment)
- [Known Limitations](#known-limitations)

---

## Why This Exists

Standard coding tests are poor proxies for AI engineering ability. They measure algorithm recall and syntax fluency, not the ability to diagnose a broken RAG pipeline, interpret model logs, or improve an LLM workflow under uncertainty.

This platform fills that gap. It simulates real AI system failures and measures how candidates investigate, iterate, and reason — capturing behavioral signals that are far more predictive of on-the-job performance than a single correct output.

---

## Features

- **Multi-tenant isolation** — each organization has its own candidates, assessments, and results with no cross-tenant data leakage
- **Candidate workspace** — prompt editor, query input, simulation output panel, logs viewer, and solution submission in one focused interface
- **Admin dashboard** — create candidates and start assessments directly from the browser, no API docs required
- **Deterministic simulation engine** — four failure modes: irrelevant retrieval, chunk boundary failure, prompt grounding failure, and low-confidence hallucination
- **Telemetry engine** — records every candidate action (prompt edits, simulation runs, log inspections, solution submissions) with monotonic timestamps
- **Evaluation engine** — explicit formulas for diagnostic accuracy, solution success, efficiency, and iteration quality
- **Scoring engine** — aggregates task scores into weighted capability profiles across four hiring-relevant dimensions
- **Session replay** — reviewers can replay any candidate's exact investigation sequence event by event
- **JWT-based auth** — role-enforced access for admins, reviewers, and candidates
- **Production ready** — Docker multi-stage build, GitHub Actions CI, structured JSON logging, health checks, rate limiting

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│         Candidate Workspace │ Reviewer Dashboard     │
└──────────────────┬──────────────────────────────────┘
                   │ JWT-authenticated API calls
┌──────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                     │
│                                                      │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Assessment │  │  Simulation  │  │  Telemetry  │  │
│  │Orchestrator│  │   Engine     │  │   Engine    │  │
│  └────────────┘  └──────────────┘  └─────────────┘  │
│  ┌────────────┐  ┌──────────────┐                    │
│  │ Evaluation │  │   Scoring    │                    │
│  │   Engine   │  │   Engine     │                    │
│  └────────────┘  └──────────────┘                    │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              PostgreSQL Database                     │
│  orgs · users · candidates · assessments · tasks    │
│  simulations · telemetry · evaluations · scores     │
└─────────────────────────────────────────────────────┘
```

**Backend subsystems:**

| Subsystem | Responsibility |
|---|---|
| `assessment/` | Task sequencing, assessment lifecycle, timeout enforcement |
| `simulation/` | Deterministic RAG scenario outputs with configurable failure modes |
| `telemetry/` | Candidate action recording scoped to org, candidate, and task run |
| `evaluation/` | Behavioral dimension scoring from telemetry and simulation history |
| `scoring/` | Capability profile aggregation across task-level evaluations |
| `routes/` | FastAPI endpoints with tenant-aware auth and consistent response envelopes |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Auth | JWT (python-jose), bcrypt |
| Frontend | React, Vite |
| Containerisation | Docker (multi-stage), Docker Compose |
| CI | GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL running locally
- Git

### 1 — Clone and set up the backend

```bash
git clone https://github.com/S-kansal/ai-assessment-platform.git
cd ai-assessment-platform

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

cd backend
pip install -r requirements.txt
```

### 2 — Configure environment variables

Copy the example env file and fill in your values:

```bash
# From the project root
copy infra\.env.example .env        # Windows
cp infra/.env.example .env          # Mac/Linux
```

At minimum set `DATABASE_URL` and `JWT_SECRET_KEY`. See [Environment Variables](#environment-variables) for the full list.

### 3 — Run database migrations

```bash
# From the backend directory
python -m alembic -c alembic.ini upgrade head
```

### 4 — Start the backend

```bash
# From the backend directory
uvicorn app.main:app --reload --port 8000
```

Confirm it is running: `http://localhost:8000/health`

### 5 — Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the app: `http://localhost:5173`

---

## Environment Variables

| Variable | Required | Description | Example |
|---|---|---|---|
| `DATABASE_URL` | ✅ | SQLAlchemy connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/ai_assessment` |
| `JWT_SECRET_KEY` | ✅ | JWT signing secret — use a long random string in production | `replace-with-random-secret` |
| `CORS_ORIGINS` | ✅ | Allowed browser origins | `["http://localhost:5173"]` |
| `ENVIRONMENT` | optional | Environment label | `development` |
| `JWT_ALGORITHM` | optional | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_MINUTES` | optional | Token lifetime in minutes | `120` |
| `ASSESSMENT_TIMEOUT_MINUTES` | optional | Max assessment duration | `60` |
| `REQUEST_RATE_LIMIT_PER_MINUTE` | optional | Per-tenant request limit | `120` |
| `EVALUATION_RATE_LIMIT_PER_MINUTE` | optional | Tighter limit for eval endpoints | `20` |
| `SIMULATION_SEED` | optional | Deterministic seed for simulation engine | `11` |
| `LOG_LEVEL` | optional | Application log level | `INFO` |
| `REDIS_URL` | optional | Reserved for future background jobs | `redis://localhost:6379/0` |

---

## Usage Walkthrough

### As an Admin

1. Go to `http://localhost:5173` and click **Register**
2. Fill in your organization name, email, and password
3. After registration you land on the **Reviewer Dashboard**
4. Click **Create Candidate**, fill in the candidate's name, email, and password
5. Click the candidate in the list, then click **Start Assessment**
6. Share the login credentials with your candidate

### As a Candidate

1. Go to `http://localhost:5173` and log in with the credentials provided
2. You land on the **Assessment Workspace**
3. Read the task description in the top-left panel
4. Edit the prompt, enter a query, and click **Run Simulation**
5. Inspect the simulation output, retrieved chunks, and logs
6. Iterate — change your prompt, re-run, observe how the failure mode responds
7. When you have identified the root cause, fill in the solution fields and click **Submit Task**
8. Repeat for each subsequent task until the assessment is complete

### As a Reviewer

1. Log in as admin and open the **Reviewer Dashboard**
2. Click any candidate to see their capability profile and scores
3. Scroll down to Task Runs to see per-task scores
4. Click any task run to load the Session Replay
5. Telemetry events and simulation runs are shown in full detail

---

## API Reference

All routes require `Authorization: Bearer <token>` except where noted as public.

### Auth
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Returns JWT for admin, reviewer, or candidate |

### Organizations
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/organizations/register` | Public | Creates org and first admin account |
| GET | `/api/organizations/me` | Any auth | Returns current user's organization |

### Candidates
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/candidates` | Admin | Creates candidate account |
| GET | `/api/candidates` | Admin/Reviewer | Lists candidates in current org |
| GET | `/api/candidates/{id}` | Admin/Reviewer/Self | Returns single candidate |

### Assessments
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/assessments` | Admin | Creates assessment |
| POST | `/assessments/{id}/start` | Admin | Starts assessment and returns first task run |
| GET | `/api/assessments/{id}` | Admin/Reviewer | Returns assessment progress |
| POST | `/api/assessments/{id}/submit` | Candidate | Submits current task, advances or completes |
| POST | `/api/assessments/{id}/timeout` | Admin | Closes timed-out assessment |

### Simulations & Tasks
| Method | Route | Access | Description |
|---|---|---|---|
| GET | `/api/tasks/{task_run_id}` | Candidate | Returns task context |
| POST | `/api/simulations/run` | Candidate | Runs deterministic RAG simulation |

### Telemetry
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/telemetry` | Candidate | Records a telemetry event |
| GET | `/api/telemetry/{task_run_id}` | Admin/Reviewer | Returns task-run event stream |

### Evaluation & Scoring
| Method | Route | Access | Description |
|---|---|---|---|
| POST | `/api/evaluations/{task_run_id}/run` | Admin | Recomputes task evaluation |
| GET | `/api/evaluations/{task_run_id}` | Admin/Reviewer | Returns stored evaluation |
| POST | `/api/scores/{assessment_id}/compute` | Admin | Recomputes capability scores |
| GET | `/api/scores/{assessment_id}` | Admin/Reviewer | Returns capability profile |

### Dashboard
| Method | Route | Access | Description |
|---|---|---|---|
| GET | `/api/dashboard/candidates` | Admin/Reviewer | Candidate list |
| GET | `/api/dashboard/candidates/{id}/profile` | Admin/Reviewer | Scores and assessment summary |
| GET | `/api/dashboard/candidates/{id}/task-runs` | Admin/Reviewer | Per-task performance rows |
| GET | `/api/dashboard/task-runs/{id}/replay` | Admin/Reviewer | Full replay data |

---

## Assessment Lifecycle

```
Admin registers org
        │
Admin creates candidate
        │
Admin starts assessment ──► Orchestrator seeds task sequence
        │
Candidate logs in ──► Assessment Workspace loads first task
        │
        ▼
┌─────────────────────────────┐
│  Candidate runs simulations │◄──── Telemetry recorded per action
│  Candidate inspects logs    │
│  Candidate iterates prompt  │
│  Candidate submits solution │
└──────────────┬──────────────┘
               │
Orchestrator evaluates task ──► Advances to next task or completes
               │
       ┌───────▼────────┐
       │  All tasks done │
       └───────┬─────────┘
               │
Scoring engine computes capability profile
               │
Reviewer dashboard shows scores + replay
```

---

## Evaluation and Scoring

Each submitted task is scored across four dimensions:

| Dimension | What it measures |
|---|---|
| **Diagnostic Accuracy** | Did the candidate correctly identify the root failure mode? |
| **Solution Success** | Did the final system behavior satisfy the task success criteria? |
| **Efficiency** | How economically did the candidate reach a conclusion? |
| **Iteration Quality** | Did the candidate follow an evidence-led, structured investigation? |

Task-level dimension scores are then aggregated into four capability areas:

| Capability | Hiring signal |
|---|---|
| **RAG Debugging** | Ability to diagnose retrieval and generation failures |
| **Prompt Engineering** | Ability to improve model behavior through prompt revision |
| **Systematic Diagnostic Reasoning** | Structured, evidence-grounded investigation process |
| **Efficiency Under Ambiguity** | Convergence speed under incomplete information |

---

## Deployment

### Docker (recommended)

```bash
# Build and start everything
docker compose -f infra/docker-compose.yml up --build
```

This starts the FastAPI backend (with built frontend served statically), PostgreSQL, and Redis on port 8000.

Run migrations before first use:

```bash
docker compose -f infra/docker-compose.yml exec backend \
  python -m alembic -c alembic.ini upgrade head
```

### Production checklist

- [ ] Set a strong random `JWT_SECRET_KEY`
- [ ] Use a managed PostgreSQL instance
- [ ] Set `CORS_ORIGINS` to your actual frontend domain
- [ ] Serve over HTTPS
- [ ] Run behind a reverse proxy (nginx, Caddy, or a managed load balancer)
- [ ] Run Alembic migrations before each deploy
- [ ] Set up automated database backups

---

## Known Limitations

- **Synchronous evaluation** — evaluation and scoring run in the web process. Acceptable for low volume; a background job queue (Celery + Redis) is the right next step for production scale.
- **No email invitations** — candidate accounts are created by admins and credentials are shared manually. An invitation flow is planned.
- **No assessment templates** — all assessments use the default task sequence. A template library is planned.
- **No exportable reports** — capability profiles are visible in the dashboard but not yet exportable to PDF or CSV.

---

## License

MIT

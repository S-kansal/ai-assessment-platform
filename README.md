# AI Engineering Assessment Platform

## Overview
AI Engineering Assessment Platform is a multi-tenant SaaS system for evaluating AI application engineers through deterministic debugging tasks instead of conventional coding quizzes. Candidates interact with simulated broken RAG pipelines, revise prompts, inspect logs, and submit diagnoses while the platform records their behavior and evaluates both process and outcome. The system is built for organizations that need evidence about real AI-system debugging ability, not just theoretical knowledge. The repository includes a FastAPI backend, a React frontend, deployment assets, and architecture documentation.

## Features
- Multi-tenant organizations, users, and candidate accounts with JWT-based role enforcement.
- Candidate assessment workspace for prompt editing, query submission, simulation runs, telemetry capture, and solution submission.
- Deterministic simulation engine for irrelevant retrieval, incorrect chunking, prompt grounding failure, and low-confidence hallucination.
- Telemetry engine that stores prompt edits, query submissions, log inspections, simulation views, and submissions against the active task run.
- Evaluation engine with explicit formulas for diagnostic accuracy, solution success, efficiency, and iteration quality.
- Scoring engine that aggregates task-level results into weighted capability profiles.
- Reviewer dashboard for candidate lists, capability profiles, task drill-down, and session replay.
- Health checks, rate limiting, request IDs, Docker assets, and GitHub Actions CI configuration.

## Architecture
The backend is organized around explicit subsystems. `assessment/` manages task sequencing and assessment lifecycle state. `simulation/` produces deterministic outputs for predefined RAG scenarios and failure modes. `telemetry/` records candidate actions as organization-owned events. `evaluation/` transforms task telemetry plus simulation history into deterministic behavioral scores. `scoring/` aggregates task evaluations into candidate capability profiles. `routes/` exposes these services through FastAPI with tenant-aware auth and consistent response envelopes.

The frontend is a standard React application built with Vite. It provides a candidate workspace that exercises the assessment flow and a reviewer dashboard that reads candidate, replay, and scoring data from the backend. API requests are scoped by JWT, and the client routes separate candidate and reviewer experiences by role.

## Local Development Setup
Clone the repository and install the backend dependencies:

```bash
git clone <repo-url>
cd ai-assessment-platform
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a local environment file from the example values:

```bash
copy infra\.env.example .env
```

Run the initial migration:

```bash
alembic -c backend/alembic.ini upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
- `ENVIRONMENT` (required in shared deployments, optional locally): application environment label. Example: `development`
- `DEBUG` (optional): enables debug-oriented error detail. Example: `false`
- `API_PREFIX` (optional): route prefix for the HTTP API. Example: `/api`
- `FRONTEND_URL` (optional): canonical frontend base URL. Example: `http://localhost:5173`
- `CORS_ORIGINS` (required for browser access): JSON-style list of allowed origins. Example: `["http://localhost:5173","http://127.0.0.1:5173"]`
- `DATABASE_URL` (required): SQLAlchemy database URL. Example: `postgresql+psycopg://postgres:postgres@localhost:5432/ai_assessment`
- `REDIS_URL` (optional): reserved for future background or caching infrastructure. Example: `redis://localhost:6379/0`
- `JWT_SECRET_KEY` (required): JWT signing key. Example: `replace-me-with-a-long-random-secret`
- `JWT_ALGORITHM` (optional): JWT signing algorithm. Example: `HS256`
- `JWT_ACCESS_TOKEN_MINUTES` (optional): token lifetime in minutes. Example: `120`
- `REQUEST_RATE_LIMIT_PER_MINUTE` (optional): per-tenant per-endpoint request limit. Example: `120`
- `EVALUATION_RATE_LIMIT_PER_MINUTE` (optional): tighter limit for evaluation endpoints. Example: `20`
- `ASSESSMENT_TIMEOUT_MINUTES` (optional): maximum duration for an assessment. Example: `60`
- `DEFAULT_SEQUENCE_MODE` (optional): default task ordering mode. Example: `fixed`
- `SIMULATION_SEED` (optional): deterministic seed used by the simulation engine. Example: `11`
- `LOG_LEVEL` (optional): application log level. Example: `INFO`

## API Overview
Authentication routes live under `/api/auth` and are public only for login. The main endpoint is `POST /api/auth/login`, which returns the JWT used by all protected routes.

Organization routes live under `/api/organizations`. `POST /api/organizations/register` creates the organization and first admin, and `GET /api/organizations/me` returns the authenticated tenant.

Candidate routes live under `/api/candidates`. `POST /api/candidates` creates candidate accounts, `GET /api/candidates` lists candidates for the current organization, and `GET /api/candidates/{candidate_id}` returns one candidate while enforcing candidate self-access limits.

Assessment routes live under `/api/assessments`. `POST /api/assessments` creates and starts an assessment, `GET /api/assessments/{assessment_id}` returns progress, `POST /api/assessments/{assessment_id}/submit` submits the current task and advances the flow, and `POST /api/assessments/{assessment_id}/timeout` closes timed-out sessions.

Task and simulation routes live under `/api/tasks` and `/api/simulations`. `GET /api/tasks/{task_run_id}` returns task context, and `POST /api/simulations/run` executes the deterministic RAG simulation for a task run.

Telemetry routes live under `/api/telemetry`. `POST /api/telemetry` records a telemetry event and `GET /api/telemetry/{task_run_id}` returns task-run events.

Evaluation and scoring routes live under `/api/evaluations` and `/api/scores`. `POST /api/evaluations/{task_run_id}/run` recomputes task evaluation, `GET /api/evaluations/{task_run_id}` reads it, `POST /api/scores/{assessment_id}/compute` recomputes scoring, and `GET /api/scores/{assessment_id}` reads the stored capability profile.

Reviewer dashboard routes live under `/api/dashboard`. `GET /api/dashboard/candidates` returns the candidate list, `GET /api/dashboard/candidates/{candidate_id}/profile` returns the high-level score view, `GET /api/dashboard/candidates/{candidate_id}/task-runs` provides task-level drill-down, and `GET /api/dashboard/task-runs/{task_run_id}/replay` returns replay data.

## Assessment Lifecycle
An organization admin registers a tenant and creates candidate accounts. Each candidate signs in with a candidate-role JWT, then starts an assessment that binds the candidate, organization, browser session, and task sequence into one assessment record. The orchestrator creates the first task run and the candidate opens the task context through the tasks API.

While the candidate works, the frontend alternates between simulation runs and telemetry writes. Simulation requests produce deterministic outputs based on the task scenario and active failure modes. Telemetry captures prompt edits, query submissions, log inspections, simulation views, and solution submissions with monotonic timestamps so the system can replay the candidate's behavior later.

When the candidate submits a task, the orchestrator closes that task run, evaluates it, and either opens the next task run or completes the assessment. The evaluation engine computes explicit dimension scores for diagnostic accuracy, solution success, efficiency, and iteration quality. After the final task, the scoring engine aggregates those task results into weighted raw and normalized capability scores that reviewers can inspect in the dashboard.

## Deployment
The repository includes Docker assets under `infra/`. Build the backend image with `docker build -f infra/Dockerfile -t ai-assessment-platform .` or use `docker compose -f infra/docker-compose.yml up --build` to start the API, PostgreSQL, and Redis together. Set production environment variables through your deployment platform, run `alembic -c backend/alembic.ini upgrade head` against the target database before starting the application, and serve the frontend with `npm run build` output behind the same API base path or a reverse proxy.

# API

All API routes are served under `/api`. Successful responses use a `{ "data": ..., "meta": {} }` envelope. Errors use a stable `{ "error": { "code", "message", "details" }, "meta": { "request_id" } }` shape.

## Auth

- `POST /api/auth/login`
  Authenticates an admin, reviewer, or candidate and returns a JWT containing `sub`, `organization_id`, `role`, and optional `candidate_id`.

## Organizations

- `POST /api/organizations/register`
  Creates an organization plus its first admin user.
- `GET /api/organizations/me`
  Returns the authenticated user's organization.

## Candidates

- `POST /api/candidates`
  Admin-only route that creates a candidate profile and candidate login.
- `GET /api/candidates`
  Reviewer and admin route for listing candidates in the current organization.
- `GET /api/candidates/{candidate_id}`
  Returns a single candidate. Candidate users can access only their own record.

## Assessments

- `POST /api/assessments`
  Creates and starts an assessment for a candidate.
- `GET /api/assessments/{assessment_id}`
  Returns assessment status and the active task run.
- `POST /api/assessments/{assessment_id}/submit`
  Submits the current task, runs evaluation, and advances to the next task or completes the assessment.
- `POST /api/assessments/{assessment_id}/timeout`
  Reviewer/admin route to close an assessment as timed out.

## Tasks and Simulations

- `GET /api/tasks/{task_run_id}`
  Returns task definition data for a specific task run.
- `POST /api/simulations/run`
  Executes the deterministic simulation for a task run and stores a `simulation_run` record.

## Telemetry

- `POST /api/telemetry`
  Stores a validated telemetry event.
- `GET /api/telemetry/{task_run_id}`
  Returns telemetry events for a task run.

## Evaluation and Scoring

- `POST /api/evaluations/{task_run_id}/run`
  Reviewer/admin route to recompute a task evaluation.
- `GET /api/evaluations/{task_run_id}`
  Returns the stored evaluation result for a task run.
- `POST /api/scores/{assessment_id}/compute`
  Recomputes assessment scoring.
- `GET /api/scores/{assessment_id}`
  Returns the stored scoring result.

## Dashboard

- `GET /api/dashboard/candidates`
  Reviewer/admin candidate list.
- `GET /api/dashboard/candidates/{candidate_id}/profile`
  Candidate capability profile and assessment summary.
- `GET /api/dashboard/candidates/{candidate_id}/task-runs`
  Task-level drill-down.
- `GET /api/dashboard/task-runs/{task_run_id}/replay`
  Replay payload including telemetry, simulations, and evaluation evidence.

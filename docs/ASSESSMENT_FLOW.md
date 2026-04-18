# Assessment Flow

1. An organization registers through `POST /api/organizations/register`. The platform creates the tenant record and the first admin user.
2. The admin creates candidate accounts with `POST /api/candidates`. Each candidate receives both a candidate profile and a candidate-role login.
3. A candidate signs in with `POST /api/auth/login`, receiving a JWT that carries organization and candidate identity.
4. The candidate starts an assessment through `POST /api/assessments`. The assessment orchestrator seeds the task catalog for that organization, assigns a task sequence, creates the assessment record, and opens the first `task_run`.
5. The candidate fetches task context with `GET /api/tasks/{task_run_id}` and begins interacting with the simulated system.
6. Each simulation request goes through `POST /api/simulations/run`. The simulation engine loads the scenario, applies the task's failure modes deterministically, returns retrieved chunks, logs, response text, and confidence, and stores a `simulation_run`.
7. The frontend records behavior through `POST /api/telemetry`. The telemetry engine captures prompt edits, query submissions, log inspections, simulation views, and solution submissions with monotonic timestamps tied to the task run, assessment, candidate, and organization.
8. When the candidate submits a task through `POST /api/assessments/{assessment_id}/submit`, the orchestrator closes that task run, evaluates it with the rule-based evaluation engine, and either opens the next task run or completes the assessment.
9. Once the final task is submitted, the scoring engine aggregates evaluation dimensions into raw and normalized capability scores for RAG debugging, prompt engineering, systematic diagnostic reasoning, and efficiency under ambiguity.
10. Reviewers and admins inspect results through the dashboard routes. They can view the candidate list, open capability profiles, drill into task-level evidence, and replay the full behavioral timeline for a task run.

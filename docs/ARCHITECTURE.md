# Architecture

The platform is split into a FastAPI backend and a React frontend. The backend owns authentication, task orchestration, deterministic simulation, telemetry capture, evaluation, scoring, and reviewer-facing data access. The frontend provides two focused surfaces: a candidate workspace for running debugging tasks and a reviewer dashboard for inspecting outcomes and replaying behavior.

The backend is intentionally organized by subsystem. `core/` holds configuration, security, dependency injection, and exception handling. `models/` and `schemas/` define the persistence and transport contracts. `simulation/` implements deterministic RAG failure modes and scenarios. `evaluation/` converts task telemetry and simulation history into explicit dimension scores. `scoring/` aggregates those task-level evaluations into candidate capability profiles. `assessment/` sequences tasks and manages lifecycle transitions.

Every persisted object is organization-owned. Tenant isolation is enforced in the database schema, in service-layer query filters, and in JWT-derived route authorization. Reviewers and admins can access only resources inside their organization, while candidate access is limited to the candidate record linked to their authenticated user.

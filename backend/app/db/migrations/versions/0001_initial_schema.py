"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=False)

    op.create_table(
        "candidates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_candidates_org_email"),
    )
    op.create_index("ix_candidates_organization_id", "candidates", ["organization_id"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_candidate_id", "users", ["candidate_id"], unique=False)
    op.create_index("ix_users_organization_id", "users", ["organization_id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("failure_modes", sa.JSON(), nullable=False),
        sa.Column("expected_diagnostic_path", sa.JSON(), nullable=False),
        sa.Column("scoring_rubric", sa.JSON(), nullable=False),
        sa.Column("scenario_key", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tasks_organization_id", "tasks", ["organization_id"], unique=False)

    op.create_table(
        "assessments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("order_mode", sa.String(length=32), nullable=False),
        sa.Column("task_ids", sa.JSON(), nullable=False),
        sa.Column("current_task_index", sa.Integer(), nullable=False),
        sa.Column("browser_session_id", sa.String(length=64), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assessments_browser_session_id", "assessments", ["browser_session_id"], unique=False)
    op.create_index("ix_assessments_candidate_id", "assessments", ["candidate_id"], unique=False)
    op.create_index("ix_assessments_organization_id", "assessments", ["organization_id"], unique=False)

    op.create_table(
        "task_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("final_prompt", sa.Text(), nullable=True),
        sa.Column("final_query", sa.Text(), nullable=True),
        sa.Column("submitted_root_cause", sa.Text(), nullable=True),
        sa.Column("submitted_fix_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_runs_assessment_id", "task_runs", ["assessment_id"], unique=False)
    op.create_index("ix_task_runs_candidate_id", "task_runs", ["candidate_id"], unique=False)
    op.create_index("ix_task_runs_organization_id", "task_runs", ["organization_id"], unique=False)
    op.create_index("ix_task_runs_task_id", "task_runs", ["task_id"], unique=False)

    op.create_table(
        "simulation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("task_run_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("retrieved_chunks", sa.JSON(), nullable=False),
        sa.Column("debug_logs", sa.JSON(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("output_quality", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_simulation_runs_assessment_id", "simulation_runs", ["assessment_id"], unique=False)
    op.create_index("ix_simulation_runs_candidate_id", "simulation_runs", ["candidate_id"], unique=False)
    op.create_index("ix_simulation_runs_organization_id", "simulation_runs", ["organization_id"], unique=False)
    op.create_index("ix_simulation_runs_task_run_id", "simulation_runs", ["task_run_id"], unique=False)

    op.create_table(
        "telemetry_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("task_run_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("monotonic_timestamp_ms", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_telemetry_events_assessment_id", "telemetry_events", ["assessment_id"], unique=False)
    op.create_index("ix_telemetry_events_candidate_id", "telemetry_events", ["candidate_id"], unique=False)
    op.create_index("ix_telemetry_events_event_type", "telemetry_events", ["event_type"], unique=False)
    op.create_index("ix_telemetry_events_organization_id", "telemetry_events", ["organization_id"], unique=False)
    op.create_index("ix_telemetry_events_session_id", "telemetry_events", ["session_id"], unique=False)
    op.create_index("ix_telemetry_events_task_run_id", "telemetry_events", ["task_run_id"], unique=False)

    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("task_run_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("dimension_scores", sa.JSON(), nullable=False),
        sa.Column("formulas", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["task_run_id"], ["task_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_run_id"),
    )
    op.create_index("ix_evaluation_results_assessment_id", "evaluation_results", ["assessment_id"], unique=False)
    op.create_index("ix_evaluation_results_candidate_id", "evaluation_results", ["candidate_id"], unique=False)
    op.create_index("ix_evaluation_results_organization_id", "evaluation_results", ["organization_id"], unique=False)
    op.create_index("ix_evaluation_results_task_run_id", "evaluation_results", ["task_run_id"], unique=False)

    op.create_table(
        "scoring_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("assessment_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("raw_scores", sa.JSON(), nullable=False),
        sa.Column("normalized_scores", sa.JSON(), nullable=False),
        sa.Column("aggregate_score", sa.Float(), nullable=False),
        sa.Column("weighting_version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"]),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("assessment_id"),
    )
    op.create_index("ix_scoring_results_assessment_id", "scoring_results", ["assessment_id"], unique=False)
    op.create_index("ix_scoring_results_candidate_id", "scoring_results", ["candidate_id"], unique=False)
    op.create_index("ix_scoring_results_organization_id", "scoring_results", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_scoring_results_organization_id", table_name="scoring_results")
    op.drop_index("ix_scoring_results_candidate_id", table_name="scoring_results")
    op.drop_index("ix_scoring_results_assessment_id", table_name="scoring_results")
    op.drop_table("scoring_results")

    op.drop_index("ix_evaluation_results_task_run_id", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_organization_id", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_candidate_id", table_name="evaluation_results")
    op.drop_index("ix_evaluation_results_assessment_id", table_name="evaluation_results")
    op.drop_table("evaluation_results")

    op.drop_index("ix_telemetry_events_task_run_id", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_session_id", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_organization_id", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_event_type", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_candidate_id", table_name="telemetry_events")
    op.drop_index("ix_telemetry_events_assessment_id", table_name="telemetry_events")
    op.drop_table("telemetry_events")

    op.drop_index("ix_simulation_runs_task_run_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_organization_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_candidate_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_assessment_id", table_name="simulation_runs")
    op.drop_table("simulation_runs")

    op.drop_index("ix_task_runs_task_id", table_name="task_runs")
    op.drop_index("ix_task_runs_organization_id", table_name="task_runs")
    op.drop_index("ix_task_runs_candidate_id", table_name="task_runs")
    op.drop_index("ix_task_runs_assessment_id", table_name="task_runs")
    op.drop_table("task_runs")

    op.drop_index("ix_assessments_organization_id", table_name="assessments")
    op.drop_index("ix_assessments_candidate_id", table_name="assessments")
    op.drop_index("ix_assessments_browser_session_id", table_name="assessments")
    op.drop_table("assessments")

    op.drop_index("ix_tasks_organization_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_index("ix_users_candidate_id", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_candidates_organization_id", table_name="candidates")
    op.drop_table("candidates")

    op.drop_index("ix_organizations_slug", table_name="organizations")
    op.drop_table("organizations")

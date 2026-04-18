"""widen simulation seed and telemetry timestamp columns

Revision ID: 0002_bigints
Revises: 0001_initial_schema
Create Date: 2026-04-18
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_bigints"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "simulation_runs",
        "seed",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using="seed::bigint",
    )
    op.alter_column(
        "telemetry_events",
        "monotonic_timestamp_ms",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        postgresql_using="monotonic_timestamp_ms::bigint",
    )


def downgrade() -> None:
    op.alter_column(
        "telemetry_events",
        "monotonic_timestamp_ms",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="monotonic_timestamp_ms::integer",
    )
    op.alter_column(
        "simulation_runs",
        "seed",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="seed::integer",
    )

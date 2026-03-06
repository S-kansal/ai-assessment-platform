"""Alembic migration environment — configured for AI Assessment Platform."""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import app models so metadata is populated
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import settings
from app.database import Base

# Import all models so Base.metadata knows about them
from app.org.models import Organization  # noqa: F401
from app.auth.models import User, AuditLog  # noqa: F401
from app.models.candidate import Candidate  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.task_run import TaskRun  # noqa: F401
from app.models.telemetry import TelemetryEvent  # noqa: F401
from app.evaluation.models import EvaluationResult  # noqa: F401
from app.scoring.models import CandidateScore, TaskScore  # noqa: F401
from app.models.assessment_result import AssessmentResult  # noqa: F401
from app.assessment.models import Assessment, AssessmentTask  # noqa: F401

config = context.config

# Set the database URL from app config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

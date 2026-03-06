import os

import sentry_sdk
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.core.logging import setup_logging, get_logger
from app.core.rate_limit import limiter

# ---------------------------------------------------------------------------
# Initialize logging
# ---------------------------------------------------------------------------
setup_logging()
logger = get_logger("main")

# ---------------------------------------------------------------------------
# Sentry (if configured)
# ---------------------------------------------------------------------------
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=os.getenv("ENVIRONMENT", "development"),
    )
    logger.info("sentry_initialized", dsn=settings.SENTRY_DSN[:20] + "...")

# ---------------------------------------------------------------------------
# Import models so they register with Base.metadata before create_all
# ---------------------------------------------------------------------------
from app.org.models import Organization  # noqa: F401, E402
from app.auth.models import User, AuditLog  # noqa: F401, E402
from app.models.candidate import Candidate  # noqa: F401, E402
from app.models.session import Session  # noqa: F401, E402
from app.models.task import Task  # noqa: F401, E402
from app.models.task_run import TaskRun  # noqa: F401, E402
from app.models.telemetry import TelemetryEvent  # noqa: F401, E402
from app.evaluation.models import EvaluationResult  # noqa: F401, E402
from app.scoring.models import CandidateScore, TaskScore  # noqa: F401, E402
from app.models.assessment_result import AssessmentResult  # noqa: F401, E402
from app.assessment.models import Assessment, AssessmentTask  # noqa: F401, E402
from app.pilot.models import PilotParticipant, PilotFeedback, PilotResultsSummary  # noqa: F401, E402

# Import routers
from app.routes.health import router as health_router  # noqa: E402
from app.routes.candidate import router as candidate_router  # noqa: E402
from app.routes.telemetry import router as telemetry_router  # noqa: E402
from app.routes.simulation import router as simulation_router  # noqa: E402
from app.routes.task import router as task_router  # noqa: E402
from app.routes.evaluation import router as evaluation_router  # noqa: E402
from app.routes.scoring import router as scoring_router  # noqa: E402
from app.routes.dashboard import router as dashboard_router  # noqa: E402
from app.assessment.routes import router as assessment_router  # noqa: E402
from app.auth.routes import router as auth_router  # noqa: E402
from app.pilot.routes import router as pilot_router  # noqa: E402

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Engineering Assessment Platform",
    description="Production SaaS backend for AI engineering hiring assessments",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Prometheus metrics
# ---------------------------------------------------------------------------
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    logger.info("prometheus_metrics_enabled")
except ImportError:
    logger.warning("prometheus_not_installed", msg="pip install prometheus-fastapi-instrumentator")

# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with structured data."""
    import time
    start = time.time()
    response: Response = await call_next(request)
    duration = round(time.time() - start, 4)

    logger.info(
        "http_request",
        method=request.method,
        path=str(request.url.path),
        status=response.status_code,
        duration_s=duration,
        client=request.client.host if request.client else "unknown",
    )
    return response

# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add production security headers to every response."""
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(telemetry_router)
app.include_router(simulation_router)
app.include_router(task_router)
app.include_router(evaluation_router)
app.include_router(scoring_router)
app.include_router(dashboard_router)
app.include_router(assessment_router)
app.include_router(pilot_router)

# ---------------------------------------------------------------------------
# Create database tables on startup
# ---------------------------------------------------------------------------

Base.metadata.create_all(bind=engine)

logger.info("application_started", version="1.0.0")

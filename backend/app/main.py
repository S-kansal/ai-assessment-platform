import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.dependencies import envelope
from app.core.exceptions import register_exception_handlers
from app.db.session import engine
from app.routes import (
    assessments,
    auth,
    candidates,
    compat,
    dashboard,
    evaluations,
    organizations,
    scores,
    simulations,
    tasks,
    telemetry,
)


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(message)s",
)
logger = logging.getLogger("ai_assessment")

app = FastAPI(title=settings.app_name, debug=settings.debug)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


@app.get("/health")
def get_health() -> JSONResponse:
    database = "ok"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - defensive
        database = "error"
    return JSONResponse(
        status_code=200 if database == "ok" else 503,
        content=envelope(
            {
                "status": "ok" if database == "ok" else "degraded",
                "database": database,
                "environment": settings.environment,
            }
        ),
    )


@app.get("/health/ready")
def get_readiness() -> dict:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return envelope({"ready": True})


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(organizations.router, prefix=settings.api_prefix)
app.include_router(candidates.router, prefix=settings.api_prefix)
app.include_router(assessments.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(simulations.router, prefix=settings.api_prefix)
app.include_router(telemetry.router, prefix=settings.api_prefix)
app.include_router(evaluations.router, prefix=settings.api_prefix)
app.include_router(scores.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(compat.router)

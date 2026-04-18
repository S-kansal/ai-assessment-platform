import asyncio
import json
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.core.dependencies import envelope
from app.core.exceptions import register_exception_handlers
from app.db.session import SessionLocal, engine
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
from app.services.assessments import sweep_overdue_assessments


STANDARD_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key, value in record.__dict__.items():
            if key in STANDARD_LOG_RECORD_FIELDS or key.startswith("_"):
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        api_prefix = settings.api_prefix.lstrip("/")
        if path == api_prefix or path.startswith(f"{api_prefix}/"):
            raise HTTPException(status_code=404)

        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code != 404:
                raise
            return await super().get_response("index.html", scope)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    root_logger.addHandler(handler)

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers.clear()
    uvicorn_access_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    uvicorn_access_logger.addHandler(handler)
    uvicorn_access_logger.propagate = False


def run_timeout_sweep() -> None:
    db = SessionLocal()
    try:
        sweep_overdue_assessments(db)
    finally:
        db.close()


async def timeout_sweep_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(run_timeout_sweep)
        except Exception:
            logging.getLogger("ai_assessment").exception("timeout_sweep_failed")
        await asyncio.sleep(60)


configure_logging()
logger = logging.getLogger("ai_assessment")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    sweep_task = asyncio.create_task(timeout_sweep_loop())
    try:
        yield
    finally:
        sweep_task.cancel()
        with suppress(asyncio.CancelledError):
            await sweep_task

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
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

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

if STATIC_DIR.exists():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="static")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        api_prefix = settings.api_prefix.lstrip("/")
        if full_path == api_prefix or full_path.startswith(f"{api_prefix}/"):
            raise HTTPException(status_code=404)
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=404)
        return FileResponse(index_path)

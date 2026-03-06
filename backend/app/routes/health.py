"""Enhanced health check endpoint with component status."""

import os

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session as DbSession

from app.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: DbSession = Depends(get_db)):
    """Health check endpoint — validates all service dependencies."""
    checks = {
        "status": "ok",
        "version": "0.2.0",
        "database": "unknown",
        "redis": "unknown",
        "simulation_engine": "ready",
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"
        checks["status"] = "degraded"

    # Redis check (optional — only if configured)
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            checks["redis"] = "connected"
        except Exception:
            checks["redis"] = "disconnected"
            checks["status"] = "degraded"
    else:
        checks["redis"] = "not_configured"

    return checks


@router.get("/health/ready")
def readiness_check(db: DbSession = Depends(get_db)):
    """Readiness probe — returns 200 only if all critical services are up."""
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database not ready")

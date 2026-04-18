import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
)
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)
_rate_limit_store: dict[str, deque[float]] = defaultdict(deque)
_rate_limit_lock = Lock()


@dataclass
class AuthContext:
    user_id: str
    organization_id: str
    role: str
    email: str
    candidate_id: str | None = None


def get_db(db: Session = Depends(get_db_session)) -> Session:
    return db


def envelope(data: object, meta: dict | None = None) -> dict:
    return {"data": data, "meta": meta or {}}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    if credentials is None:
        raise AuthenticationError("Authentication is required")

    payload = decode_access_token(credentials.credentials)
    user = db.scalar(
        select(User).where(
            User.id == payload["sub"],
            User.organization_id == payload["organization_id"],
            User.is_active.is_(True),
        )
    )
    if user is None:
        raise AuthenticationError("User is no longer active")

    return AuthContext(
        user_id=user.id,
        organization_id=user.organization_id,
        role=user.role,
        email=user.email,
        candidate_id=user.candidate_id,
    )


def require_roles(*allowed_roles: str) -> Callable[[AuthContext], AuthContext]:
    def dependency(user: AuthContext = Depends(get_current_user)) -> AuthContext:
        if user.role not in allowed_roles:
            raise AuthorizationError(
                "You do not have permission to access this resource",
                {"required_roles": list(allowed_roles), "actual_role": user.role},
            )
        return user

    return dependency


def require_candidate_self(candidate_id: str, user: AuthContext) -> None:
    if user.role == "candidate" and user.candidate_id != candidate_id:
        raise AuthorizationError("Candidates can only access their own data")


def enforce_rate_limit(scope: str, limit: int) -> None:
    now = time.time()
    window_start = now - 60
    with _rate_limit_lock:
        bucket = _rate_limit_store[scope]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            raise RateLimitError(
                "Rate limit exceeded",
                {"scope": scope, "limit_per_minute": limit},
            )
        bucket.append(now)


def rate_limit_dependency(
    endpoint_key: str,
    limit: int,
) -> Callable[[AuthContext, Request], None]:
    def dependency(
        request: Request,
        user: AuthContext = Depends(get_current_user),
    ) -> None:
        scope = f"{user.organization_id}:{endpoint_key}:{request.method}"
        enforce_rate_limit(scope, limit)

    return dependency
def get_tenant_object_or_404(model: type, db: Session, object_id: str, organization_id: str):
    instance = db.scalar(
        select(model).where(
            model.id == object_id,
            model.organization_id == organization_id,
        )
    )
    if instance is None:
        raise NotFoundError(f"{model.__name__} not found")
    return instance

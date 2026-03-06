"""Tenant guard — FastAPI dependency that extracts and validates tenant context from JWT.

Usage in routes:
    from app.auth.tenant_guard import get_current_user, require_role

    @router.get("/protected")
    def protected(user=Depends(get_current_user)):
        org_id = user["organization_id"]
"""

from typing import Dict, List

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.jwt_service import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """Extract and validate user from JWT Bearer token.

    Returns dict with: user_id, organization_id, role, email
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = decode_access_token(credentials.credentials)

    required = ["user_id", "organization_id", "role"]
    for key in required:
        if key not in payload:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    return {
        "user_id": payload["user_id"],
        "organization_id": payload["organization_id"],
        "role": payload["role"],
        "email": payload.get("email", ""),
    }


def require_role(*allowed_roles: str):
    """Dependency factory that restricts access to specific roles.

    Usage:
        @router.get("/admin-only")
        def admin_only(user=Depends(require_role("admin"))):
            ...
    """
    def _check(user: Dict = Depends(get_current_user)) -> Dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user['role']}' not authorized. Required: {', '.join(allowed_roles)}",
            )
        return user
    return _check

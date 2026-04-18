import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError


PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=PBKDF2_ITERATIONS,
        salt=base64.b64encode(salt).decode("ascii"),
        digest=base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash.startswith("pbkdf2_sha256$"):
        return False
    _prefix, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
    salt = base64.b64decode(salt_b64.encode("ascii"))
    expected_digest = base64.b64decode(digest_b64.encode("ascii"))
    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        int(iterations),
    )
    return hmac.compare_digest(actual_digest, expected_digest)


def create_access_token(claims: dict[str, Any]) -> str:
    payload = claims.copy()
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_minutes
    )
    payload["exp"] = expire_at
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise AuthenticationError("Invalid or expired token") from exc

    required_claims = {"sub", "organization_id", "role"}
    if not required_claims.issubset(payload):
        raise AuthenticationError("Token is missing required claims")
    return payload

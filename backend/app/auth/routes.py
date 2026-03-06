"""Authentication API routes."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from app.database import get_db
from app.auth.auth_service import register_organization, login_user

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    company_name: str
    admin_email: str
    password: str


class RegisterResponse(BaseModel):
    organization_id: str
    organization_slug: str
    admin_user_id: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    organization_id: str
    role: str


# ---------------------------------------------------------------------------
# POST /org/register
# ---------------------------------------------------------------------------

@router.post("/org/register", response_model=RegisterResponse)
def register_org(body: RegisterRequest, db: DbSession = Depends(get_db)):
    """Register a new organization with an admin user."""
    return register_organization(db, body.company_name, body.admin_email, body.password)


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest, db: DbSession = Depends(get_db)):
    """Authenticate user and return JWT token."""
    return login_user(db, body.email, body.password)

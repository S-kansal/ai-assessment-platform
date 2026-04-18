from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import AuthContext, envelope, get_current_user, get_db
from app.schemas.organization import OrganizationRegisterRequest
from app.services.organizations import get_organization, register_organization


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/register")
def create_organization(
    body: OrganizationRegisterRequest,
    db: Session = Depends(get_db),
) -> dict:
    organization = register_organization(
        db,
        body.organization_name,
        body.organization_slug,
        body.admin_email,
        body.admin_password,
    )
    db.commit()
    return envelope(
        {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
        }
    )


@router.get("/me")
def get_my_organization(
    user: AuthContext = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    organization = get_organization(db, user.organization_id)
    return envelope(
        {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
        }
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import envelope, get_db
from app.schemas.user import UserLoginRequest
from app.services.auth import login_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(body: UserLoginRequest, db: Session = Depends(get_db)) -> dict:
    result = login_user(db, body.email, body.password)
    db.commit()
    return envelope(result)

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class OrganizationRegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    organization_slug: str = Field(min_length=2, max_length=120)
    admin_email: EmailStr
    admin_password: str = Field(min_length=8, max_length=255)


class OrganizationRead(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime

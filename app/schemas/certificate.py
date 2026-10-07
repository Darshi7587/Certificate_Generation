from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.models.certificate import CertificateStatus


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Recipient full name")
    email: EmailStr = Field(..., description="Recipient valid email address")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Recipient name cannot be empty or whitespace only")
        return stripped


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    recipient_name: str
    recipient_email: str
    status: CertificateStatus
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CertificateListResponse(BaseModel):
    job_id: str
    total: int
    certificates: List[CertificateResponse]

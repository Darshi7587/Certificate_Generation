from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.job import JobStatus
from app.schemas.certificate import RecipientCreate


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1, description="Name of the event")
    event_date: str = Field(..., min_length=1, description="Date of the event")
    certificate_title: str = Field(..., min_length=1, description="Title on certificate")
    recipients: List[RecipientCreate] = Field(..., description="List of recipient details")

    @field_validator("event_name", "event_date", "certificate_title")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace only")
        return stripped

    @field_validator("recipients")
    @classmethod
    def validate_recipients_not_empty(cls, v: List[RecipientCreate]) -> List[RecipientCreate]:
        if not v:
            raise ValueError("Recipients list cannot be empty. At least one recipient is required.")
        return v


class JobCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: JobStatus
    total_recipients: int


class JobDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    event_name: str
    event_date: str
    certificate_title: str
    status: JobStatus
    total: int
    successful: int
    failed: int
    created_at: datetime
    updated_at: datetime

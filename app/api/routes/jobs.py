from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.job import JobCreate, JobCreateResponse, JobDetailResponse
from app.schemas.certificate import CertificateListResponse, CertificateResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_bulk_job(
    job_in: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Creates a bulk certificate generation job and schedules background processing.
    """
    job = JobService.create_job(db, job_in)
    background_tasks.add_task(JobService.process_bulk_job, job.id)
    return JobCreateResponse(
        job_id=job.id,
        status=job.status,
        total_recipients=job.total_recipients,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves summary status and progress counts for a specific job.
    """
    job = JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found",
        )
    return JobDetailResponse(
        job_id=job.id,
        event_name=job.event_name,
        event_date=job.event_date,
        certificate_title=job.certificate_title,
        status=job.status,
        total=job.total_recipients,
        successful=job.successful_count,
        failed=job.failed_count,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/{job_id}/certificates", response_model=CertificateListResponse)
def get_job_certificates(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves individual certificate statuses and retrieval information for a specific job.
    """
    job = JobService.get_job(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found",
        )
    certificates = JobService.get_job_certificates(db, job_id)
    cert_responses = [CertificateResponse.model_validate(c) for c in certificates]
    return CertificateListResponse(
        job_id=job.id,
        total=len(cert_responses),
        certificates=cert_responses,
    )

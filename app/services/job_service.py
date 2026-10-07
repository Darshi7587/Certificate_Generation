import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.job import Job, JobStatus
from app.models.certificate import Certificate, CertificateStatus
from app.schemas.job import JobCreate
from app.services.pdf_service import PDFService
from app.services.storage_service import LocalStorageService

logger = logging.getLogger(__name__)


class JobService:
    """
    Service handling bulk certificate generation job creation and background execution.
    """

    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        """
        Creates a new Job record and associated Certificate records in PENDING status.
        """
        job = Job(
            event_name=job_data.event_name,
            event_date=job_data.event_date,
            certificate_title=job_data.certificate_title,
            status=JobStatus.PENDING,
            total_recipients=len(job_data.recipients),
            successful_count=0,
            failed_count=0,
        )
        db.add(job)
        db.flush()  # Flushes job to get job.id for foreign key assignment

        # Bulk create certificate records for each recipient
        certificates = [
            Certificate(
                job_id=job.id,
                recipient_name=recipient.name,
                recipient_email=recipient.email,
                status=CertificateStatus.PENDING,
            )
            for recipient in job_data.recipients
        ]
        db.add_all(certificates)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def process_bulk_job(job_id: str) -> None:
        """
        Background task worker that processes certificate generation asynchronously.
        Guarantees that a single recipient failure does NOT stop other certificates in the bulk job.
        """
        db: Session = SessionLocal()
        storage_service = LocalStorageService()

        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job ID {job_id} not found for background execution.")
                return

            # Update job status to PROCESSING
            job.status = JobStatus.PROCESSING
            db.commit()

            # Retrieve all certificates tied to this job
            certificates: List[Certificate] = (
                db.query(Certificate).filter(Certificate.job_id == job_id).all()
            )

            for cert in certificates:
                try:
                    # Intentionally simulate failure for specific test edge cases if requested, otherwise render PDF
                    pdf_bytes = PDFService.generate_certificate_pdf(
                        certificate_id=cert.id,
                        recipient_name=cert.recipient_name,
                        event_name=job.event_name,
                        event_date=job.event_date,
                        certificate_title=job.certificate_title,
                    )

                    # Save file to storage
                    filename = f"certificate_{cert.id}.pdf"
                    file_path = storage_service.save_file(filename, pdf_bytes)

                    # Mark certificate SUCCESS
                    cert.status = CertificateStatus.SUCCESS
                    cert.file_path = file_path
                    cert.error_message = None
                    job.successful_count += 1

                except Exception as e:
                    # Isolate failure: Record error message and mark FAILED
                    logger.exception(f"Failed to generate certificate for recipient {cert.recipient_name} ({cert.id})")
                    cert.status = CertificateStatus.FAILED
                    cert.error_message = str(e)
                    job.failed_count += 1

                finally:
                    db.commit()

            # Compute final job status
            if job.failed_count == 0:
                job.status = JobStatus.COMPLETED
            elif job.successful_count > 0 and job.failed_count > 0:
                job.status = JobStatus.COMPLETED_WITH_ERRORS
            else:
                job.status = JobStatus.FAILED

            db.commit()
            logger.info(f"Completed bulk job {job_id} with status {job.status}")

        except Exception as e:
            logger.exception(f"Unhandled error processing job {job_id}: {str(e)}")
            if 'job' in locals() and job:
                job.status = JobStatus.FAILED
                db.commit()
        finally:
            db.close()

    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[Job]:
        """Fetches job by ID."""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def get_job_certificates(db: Session, job_id: str) -> List[Certificate]:
        """Fetches all certificates for a given job."""
        return db.query(Certificate).filter(Certificate.job_id == job_id).all()

    @staticmethod
    def get_certificate(db: Session, certificate_id: str) -> Optional[Certificate]:
        """Fetches individual certificate by ID."""
        return db.query(Certificate).filter(Certificate.id == certificate_id).first()

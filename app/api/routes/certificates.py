import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.job_service import JobService
from app.models.certificate import CertificateStatus

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/{certificate_id}")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    """
    Downloads the generated PDF certificate by certificate ID.
    """
    cert = JobService.get_certificate(db, certificate_id)
    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' not found",
        )

    if cert.status == CertificateStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate generation failed for this recipient: {cert.error_message}",
        )

    if cert.status == CertificateStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="Certificate generation is still processing. Please try again shortly.",
        )

    if not cert.file_path or not os.path.exists(cert.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated certificate PDF file is missing on storage.",
        )

    safe_name = "".join(c for c in cert.recipient_name if c.isalnum() or c in (" ", "_", "-")).strip()
    download_filename = f"Certificate_{safe_name}.pdf"

    return FileResponse(
        path=cert.file_path,
        media_type="application/pdf",
        filename=download_filename,
    )

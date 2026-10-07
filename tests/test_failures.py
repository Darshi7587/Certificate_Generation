from unittest.mock import patch
from app.services.pdf_service import PDFService


def test_individual_certificate_failure_isolation(client):
    """
    Tests that if generating one certificate raises an exception,
    other valid certificates in the same job complete successfully,
    and the overall job status updates to COMPLETED_WITH_ERRORS.
    """
    payload = {
        "event_name": "Aereo Hackathon 2026",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Participation",
        "recipients": [
            {"name": "Rahul Sharma", "email": "rahul@example.com"},
            {"name": "FAIL_RECIPIENT", "email": "fail@example.com"},
            {"name": "Ananya Rao", "email": "ananya@example.com"},
        ],
    }

    original_generate = PDFService.generate_certificate_pdf

    def mock_generate_pdf(certificate_id, recipient_name, event_name, event_date, certificate_title):
        if recipient_name == "FAIL_RECIPIENT":
            raise RuntimeError("Simulated PDF Rendering Failure")
        return original_generate(certificate_id, recipient_name, event_name, event_date, certificate_title)

    with patch("app.services.job_service.PDFService.generate_certificate_pdf", side_effect=mock_generate_pdf):
        create_res = client.post("/api/jobs/", json=payload)
        assert create_res.status_code == 202
        job_id = create_res.json()["job_id"]

    # Verify job status summary
    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "COMPLETED_WITH_ERRORS"
    assert status_data["total"] == 3
    assert status_data["successful"] == 2
    assert status_data["failed"] == 1

    # Verify individual certificate statuses
    certs_res = client.get(f"/api/jobs/{job_id}/certificates")
    certificates = certs_res.json()["certificates"]

    rahul_cert = next(c for c in certificates if c["recipient_name"] == "Rahul Sharma")
    fail_cert = next(c for c in certificates if c["recipient_name"] == "FAIL_RECIPIENT")
    ananya_cert = next(c for c in certificates if c["recipient_name"] == "Ananya Rao")

    assert rahul_cert["status"] == "SUCCESS"
    assert fail_cert["status"] == "FAILED"
    assert "Simulated PDF Rendering Failure" in fail_cert["error_message"]
    assert ananya_cert["status"] == "SUCCESS"

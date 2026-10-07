def test_get_certificates_for_job(client):
    """Test listing certificates associated with a job."""
    payload = {
        "event_name": "Aereo AI Workshop",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Completion",
        "recipients": [
            {"name": "Rahul Sharma", "email": "rahul@example.com"},
            {"name": "Priya Kumar", "email": "priya@example.com"},
        ],
    }
    create_res = client.post("/api/jobs/", json=payload)
    job_id = create_res.json()["job_id"]

    cert_list_res = client.get(f"/api/jobs/{job_id}/certificates")
    assert cert_list_res.status_code == 200
    data = cert_list_res.json()
    assert data["job_id"] == job_id
    assert data["total"] == 2
    assert len(data["certificates"]) == 2
    assert data["certificates"][0]["status"] == "SUCCESS"


def test_download_generated_certificate(client):
    """Test downloading a successfully generated PDF certificate."""
    payload = {
        "event_name": "Aereo AI Workshop",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Completion",
        "recipients": [{"name": "Rahul Sharma", "email": "rahul@example.com"}],
    }
    create_res = client.post("/api/jobs/", json=payload)
    job_id = create_res.json()["job_id"]

    certs_res = client.get(f"/api/jobs/{job_id}/certificates")
    cert_id = certs_res.json()["certificates"][0]["id"]

    download_res = client.get(f"/api/certificates/{cert_id}")
    assert download_res.status_code == 200
    assert download_res.headers["content-type"] == "application/pdf"
    assert len(download_res.content) > 0


def test_download_nonexistent_certificate(client):
    """Test 404 response for downloading non-existent certificate."""
    res = client.get("/api/certificates/nonexistent-id-999")
    assert res.status_code == 404

def test_create_bulk_job(client):
    """Test successful job creation endpoint."""
    payload = {
        "event_name": "Aereo Hackathon 2026",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Participation",
        "recipients": [
            {"name": "Rahul Sharma", "email": "rahul@example.com"},
            {"name": "Priya Kumar", "email": "priya@example.com"},
        ],
    }
    response = client.post("/api/jobs/", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total_recipients"] == 2


def test_get_job_status(client):
    """Test fetching status for an existing job."""
    payload = {
        "event_name": "Tech Summit 2026",
        "event_date": "2026-11-15",
        "certificate_title": "Certificate of Excellence",
        "recipients": [{"name": "Ananya Rao", "email": "ananya@example.com"}],
    }
    create_res = client.post("/api/jobs/", json=payload)
    job_id = create_res.json()["job_id"]

    # TestClient automatically executes background task upon POST response completion
    status_res = client.get(f"/api/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] == "COMPLETED"
    assert status_data["total"] == 1
    assert status_data["successful"] == 1
    assert status_data["failed"] == 0


def test_get_nonexistent_job(client):
    """Test 404 response for non-existent job ID."""
    response = client.get("/api/jobs/nonexistent-uuid-123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_empty_recipients_validation(client):
    """Test rejection when recipients list is empty."""
    payload = {
        "event_name": "Aereo Hackathon 2026",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Participation",
        "recipients": [],
    }
    response = client.post("/api/jobs/", json=payload)
    assert response.status_code == 422


def test_invalid_email_validation(client):
    """Test rejection when recipient email format is invalid."""
    payload = {
        "event_name": "Aereo Hackathon 2026",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Participation",
        "recipients": [{"name": "Rahul Sharma", "email": "invalid-email"}],
    }
    response = client.post("/api/jobs/", json=payload)
    assert response.status_code == 422


def test_missing_recipient_name_validation(client):
    """Test rejection when recipient name is empty or missing."""
    payload = {
        "event_name": "Aereo Hackathon 2026",
        "event_date": "2026-10-07",
        "certificate_title": "Certificate of Participation",
        "recipients": [{"name": "   ", "email": "rahul@example.com"}],
    }
    response = client.post("/api/jobs/", json=payload)
    assert response.status_code == 422

import os
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, get_db
from app.main import app

TEST_DATABASE_FILE = "./test_certificates.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_FILE}"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_test_database():
    """Create fresh database tables before each test function and clean up afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DATABASE_FILE):
        try:
            os.remove(TEST_DATABASE_FILE)
        except Exception:
            pass


@pytest.fixture(scope="function")
def db(setup_test_database):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient with overridden get_db dependency and background SessionLocal patch."""
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with patch("app.services.job_service.SessionLocal", TestingSessionLocal):
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()

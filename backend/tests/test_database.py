import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import Base, get_db
from app.models.models import ScanRecord, CheckupRecord
from app.services.history_service import (
    save_scan_record, get_scan_history,
    save_checkup_record, get_checkup_history
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

client = TestClient(app)

def test_database_creation_and_insert_read():
    db = TestingSessionLocal()
    rec = save_scan_record(
        db=db,
        scan_type="url",
        indicator="https://example.com",
        domain="example.com",
        risk_score=15,
        risk_level="LOW",
        confidence="HIGH",
        reasons=["Clean URL"],
        evidence={"test": True}
    )
    assert rec is not None
    assert rec.id is not None
    assert rec.indicator == "https://example.com"

    history = get_scan_history(db)
    assert len(history) == 1
    assert history[0].indicator == "https://example.com"
    db.close()

def test_checkup_history_insert_read():
    db = TestingSessionLocal()
    rec = save_checkup_record(
        db=db,
        overall_score=85,
        security_level="EXCELLENT",
        weakest_category="None",
        recommendations=["Maintain hygiene"]
    )
    assert rec is not None
    assert rec.overall_score == 85

    history = get_checkup_history(db)
    assert len(history) == 1
    assert history[0].security_level == "EXCELLENT"
    db.close()

def test_history_api_endpoints():
    res_scan = client.post("/api/scan/url", json={"url": "https://example.com"})
    assert res_scan.status_code == 200

    res_scans = client.get("/api/history/scans")
    assert res_scans.status_code == 200
    scans_data = res_scans.json()
    assert len(scans_data) >= 1
    assert scans_data[0]["indicator"] == "https://example.com/"

    res_checkup = client.get("/api/history/checkups")
    assert res_checkup.status_code == 200

def test_invalid_data_handling():
    db = TestingSessionLocal()
    rec = save_scan_record(db, "url", "", None, 0, "LOW", "HIGH", [], {})
    assert rec is not None
    assert rec.to_dict()["reasons"] == []
    db.close()

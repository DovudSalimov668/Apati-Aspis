from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_scan_valid_public_url():
    response = client.post("/api/scan/url", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["ssrf_blocked"] is False
    assert data["domain"] == "example.com"
    assert "risk_score" in data
    assert "risk_level" in data

def test_scan_ssrf_localhost():
    response = client.post("/api/scan/url", json={"url": "http://localhost:8000/admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["ssrf_blocked"] is True
    assert data["risk_score"] == 100
    assert data["risk_level"] == "CRITICAL"
    assert "Blocked by SSRF Protection" in data["reasons"][0]

def test_scan_ssrf_private_ip():
    response = client.post("/api/scan/url", json={"url": "http://192.168.1.1/router"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["ssrf_blocked"] is True
    assert data["risk_score"] == 100
    assert data["risk_level"] == "CRITICAL"

def test_scan_malformed_url():
    response = client.post("/api/scan/url", json={"url": "ftp://unsupported-scheme"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["risk_score"] == 100
    assert data["risk_level"] == "CRITICAL"

def test_scan_suspicious_ip_url():
    response = client.post("/api/scan/url", json={"url": "http://93.184.216.34:8080/login.exe"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["risk_score"] >= 50
    assert data["risk_level"] in ("HIGH", "CRITICAL")

def test_demo_mode_scenarios():
    for scen in ["safe", "moderate", "high", "critical"]:
        res = client.post("/api/scan/demo", json={"scenario": scen})
        assert res.status_code == 200
        data = res.json()
        assert "[DEMO / SIMULATED RESULT]" in data["reasons"][0]
        assert "risk_score" in data
        assert "risk_level" in data

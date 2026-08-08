import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def create_dummy_image_bytes(fmt: str = "PNG", size=(100, 100)) -> bytes:
    img = Image.new("RGB", size, color="white")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

def test_plain_message_scan():
    response = client.post("/api/scan/message", json={"message": "Hello, how are you today?"})
    assert response.status_code == 200
    data = response.json()
    assert data["raw_message"] == "Hello, how are you today?"
    assert len(data["extracted_urls"]) == 0
    assert data["risk_score"] == 0
    assert data["risk_level"] == "LOW"

def test_message_with_single_url():
    msg = "Please review your statement at https://example.com"
    response = client.post("/api/scan/message", json={"message": msg})
    assert response.status_code == 200
    data = response.json()
    assert len(data["extracted_urls"]) == 1
    assert "https://example.com" in data["extracted_urls"]
    assert len(data["url_scans"]) == 1

def test_message_with_multiple_urls():
    msg = "Check https://example.com and http://93.184.216.34:8080/login.exe"
    response = client.post("/api/scan/message", json={"message": msg})
    assert response.status_code == 200
    data = response.json()
    assert len(data["extracted_urls"]) == 2
    assert len(data["url_scans"]) == 2
    assert data["risk_score"] >= 50

def test_suspicious_message_heuristics():
    msg = "URGENT: Your PayPal account has been suspended! Verify password immediately to avoid fees and wire money."
    response = client.post("/api/scan/message", json={"message": msg})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] >= 50
    assert data["risk_level"] in ("HIGH", "CRITICAL")
    codes = [h["code"] for h in data["heuristics"]]
    assert "MESSAGE_URGENCY_PRESSURE" in codes
    assert "MESSAGE_CREDENTIAL_REQUEST" in codes

def test_message_with_ssrf_url():
    msg = "Click here to login: http://127.0.0.1:8000/admin"
    response = client.post("/api/scan/message", json={"message": msg})
    assert response.status_code == 200
    data = response.json()
    assert len(data["url_scans"]) == 1
    assert data["url_scans"][0]["ssrf_blocked"] is True

def test_invalid_qr_image():
    dummy_bytes = create_dummy_image_bytes("PNG")
    response = client.post("/api/scan/qr", files={"file": ("test.png", dummy_bytes, "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 100
    assert "No valid QR code detected" in data["reasons"][0]

def test_oversized_file_rejection():
    # 6MB dummy buffer
    big_bytes = b"0" * (6 * 1024 * 1024)
    response = client.post("/api/scan/qr", files={"file": ("big.png", big_bytes, "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 100
    assert "exceeds 5MB limit" in data["reasons"][0]

def test_invalid_image_format_rejection():
    invalid_bytes = b"NOT_AN_IMAGE_HEADER_DATA"
    response = client.post("/api/scan/qr", files={"file": ("test.txt", invalid_bytes, "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 100

def test_image_ocr_endpoint_degradation():
    dummy_bytes = create_dummy_image_bytes("PNG")
    response = client.post("/api/scan/image", files={"file": ("test.png", dummy_bytes, "image/png")})
    assert response.status_code == 200
    data = response.json()
    assert data["ocr_status"] in ("COMPLETED", "OCR_UNAVAILABLE")

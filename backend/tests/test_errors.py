from fastapi import APIRouter
from fastapi.testclient import TestClient
from app.main import app
from app.core.errors import NotFoundException, ValidationException

error_test_router = APIRouter(prefix="/test-errors")

@error_test_router.get("/not-found")
def trigger_not_found():
    raise NotFoundException("Custom resource not found")

@error_test_router.get("/validation")
def trigger_validation():
    raise ValidationException("Custom validation failed")

app.include_router(error_test_router)


client = TestClient(app)

def test_custom_not_found_exception():
    response = client.get("/test-errors/not-found")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert data["error"]["message"] == "Custom resource not found"

def test_custom_validation_exception():
    response = client.get("/test-errors/validation")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Custom validation failed"

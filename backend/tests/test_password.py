import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.services.password_service import check_password_pwned

client = TestClient(app)

@pytest.mark.asyncio
async def test_known_leaked_password_pwned():
    # password123 SHA-1 is CBFDAC6008F9CAB4083784CBD1874F76618D2A97
    # Prefix: CBFDA, Suffix: C6008F9CAB4083784CBD1874F76618D2A97
    mock_resp_text = "C6008F9CAB4083784CBD1874F76618D2A97:4582910\n1234567890ABCDEF1234567890ABCDEF1234567:10"
    mock_resp = MagicMock()


    mock_resp.status_code = 200
    mock_resp.text = mock_resp_text

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_resp

        res = await check_password_pwned("password123")
        assert res.is_pwned is True
        assert res.breach_count == 4582910
        assert res.sha1_prefix == "CBFDA"
        assert "appeared in public data breaches" in res.message


@pytest.mark.asyncio
async def test_unpwned_complex_password():
    mock_resp_text = "00000000000000000000000000000000000:5"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = mock_resp_text

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_resp

        res = await check_password_pwned("SuperSecretUnpwnedPass9988#$!")
        assert res.is_pwned is False
        assert res.breach_count == 0
        assert "No match found" in res.message
        assert "does NOT guarantee" in res.disclaimer

def test_password_check_api_endpoint():
    response = client.post("/api/password/check", json={"password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "is_pwned" in data
    assert "disclaimer" in data
    # Plaintext password is never echoed back in API response
    assert "password" not in data

def test_password_empty_validation():
    response = client.post("/api/password/check", json={"password": ""})
    assert response.status_code == 422

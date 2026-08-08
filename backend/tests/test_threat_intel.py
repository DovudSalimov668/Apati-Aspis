import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from app.services.threat_intel.base import ProviderState, ProviderResult
from app.services.threat_intel.safe_browsing import GoogleSafeBrowsingProvider
from app.services.threat_intel.urlhaus import URLhausProvider
from app.services.threat_intel.virustotal import VirusTotalProvider
from app.services.threat_intel.manager import ThreatIntelManager

def create_mock_response(status_code: int = 200, json_data: dict = None):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json = MagicMock(return_value=json_data or {})
    return mock_resp

@pytest.mark.asyncio
async def test_safe_browsing_match():
    provider = GoogleSafeBrowsingProvider(api_key="test_key")
    mock_json = {
        "matches": [
            {
                "threatType": "MALWARE",
                "platformType": "ANY_PLATFORM",
                "threatEntryType": "URL",
                "threat": {"url": "http://malware.example.com"}
            }
        ]
    }
    mock_resp = create_mock_response(200, mock_json)
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_resp

        res = await provider.check_url("http://malware.example.com", "malware.example.com")
        assert res.state == ProviderState.MATCH
        assert res.threat_type == "MALWARE"

@pytest.mark.asyncio
async def test_safe_browsing_no_match():
    provider = GoogleSafeBrowsingProvider(api_key="test_key")
    mock_json = {"matches": []}
    mock_resp = create_mock_response(200, mock_json)
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_resp

        res = await provider.check_url("http://safe.example.com", "safe.example.com")
        assert res.state == ProviderState.NO_MATCH

@pytest.mark.asyncio
async def test_urlhaus_match():
    provider = URLhausProvider()
    mock_json = {
        "query_status": "ok",
        "url_status": "online",
        "threat": "malware_download",
        "reporter": "abuse_ch"
    }
    mock_resp = create_mock_response(200, mock_json)
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_resp

        res = await provider.check_url("http://malware-distributor.example.com/payload.exe", "malware-distributor.example.com")
        assert res.state == ProviderState.MATCH
        assert res.threat_type == "malware_download"

@pytest.mark.asyncio
async def test_urlhaus_no_match():
    provider = URLhausProvider()
    mock_json = {
        "query_status": "no_results"
    }
    mock_resp = create_mock_response(200, mock_json)
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_resp

        res = await provider.check_url("http://safe.example.com", "safe.example.com")
        assert res.state == ProviderState.NO_MATCH

@pytest.mark.asyncio
async def test_virustotal_missing_api_key():
    provider = VirusTotalProvider(api_key="")
    res = await provider.check_url("http://example.com", "example.com")
    assert res.state == ProviderState.UNAVAILABLE
    assert "not configured" in res.error_message

@pytest.mark.asyncio
async def test_virustotal_match_with_key():
    provider = VirusTotalProvider(api_key="mock_vt_key")
    mock_json = {
        "data": {
            "attributes": {
                "last_analysis_stats": {
                    "malicious": 15,
                    "suspicious": 2,
                    "harmless": 50,
                    "undetected": 5
                }
            }
        }
    }
    mock_resp = create_mock_response(200, mock_json)
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_resp

        res = await provider.check_url("http://malicious.example.com", "malicious.example.com")
        assert res.state == ProviderState.MATCH
        assert res.details["malicious"] == 15

@pytest.mark.asyncio
async def test_provider_timeout_handling():
    provider = GoogleSafeBrowsingProvider(api_key="key")
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        res = await provider.check_url("http://slow-site.example.com", "slow-site.example.com")
        assert res.state == ProviderState.UNAVAILABLE
        assert "timed out" in res.error_message

@pytest.mark.asyncio
async def test_provider_rate_limited():
    provider = URLhausProvider()
    mock_resp = create_mock_response(429, {})
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_resp

        res = await provider.check_url("http://busy.example.com", "busy.example.com")
        assert res.state == ProviderState.RATE_LIMITED

@pytest.mark.asyncio
async def test_threat_intel_manager_concurrency():
    manager = ThreatIntelManager()
    with patch("app.services.threat_intel.safe_browsing.GoogleSafeBrowsingProvider.check_url", new_callable=AsyncMock) as mock_sb, \
         patch("app.services.threat_intel.urlhaus.URLhausProvider.check_url", new_callable=AsyncMock) as mock_urlhaus:
        
        mock_sb.return_value = ProviderResult("GoogleSafeBrowsing", ProviderState.MATCH, threat_type="MALWARE")
        mock_urlhaus.return_value = ProviderResult("URLhaus", ProviderState.NO_MATCH)

        res = await manager.query_all("http://test.example.com", "test.example.com")
        assert res["has_match"] is True
        assert "GoogleSafeBrowsing" in res["match_providers"]
        assert "GoogleSafeBrowsing" in res["providers"]
        assert "URLhaus" in res["providers"]

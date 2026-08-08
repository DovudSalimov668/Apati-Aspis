import httpx
from typing import Optional
from app.services.threat_intel.base import ThreatIntelProvider, ProviderResult, ProviderState

class GoogleSafeBrowsingProvider(ThreatIntelProvider):
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 2.5):
        enabled = bool(api_key and api_key.strip())
        super().__init__(name="GoogleSafeBrowsing", enabled=enabled, timeout_seconds=timeout_seconds)
        self.api_key = api_key.strip() if api_key else ""
        self.endpoint = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

    async def check_url(self, target_url: str, domain: str) -> ProviderResult:
        if not self.enabled or not self.api_key:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="Google Safe Browsing API key not configured"
            )

        payload = {
            "client": {
                "clientId": "apati-aspis",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": target_url}
                ]
            }
        }

        url_with_key = f"{self.endpoint}?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(url_with_key, json=payload)

                if response.status_code == 429:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.RATE_LIMITED,
                        error_message="Google Safe Browsing API rate limit reached"
                    )

                if response.status_code != 200:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.UNAVAILABLE,
                        error_message=f"Google Safe Browsing HTTP status {response.status_code}"
                    )

                data = response.json()
                matches = data.get("matches", [])

                if matches:
                    threat_type = matches[0].get("threatType", "MALICIOUS")
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.MATCH,
                        threat_type=threat_type,
                        details={"matches": matches},
                        raw_response=data
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.NO_MATCH,
                        details={"matches": []},
                        raw_response=data
                    )

        except httpx.TimeoutException:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="Google Safe Browsing query timed out"
            )
        except httpx.RequestError as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message=f"Google Safe Browsing connection error: {str(exc)}"
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.ERROR,
                error_message=f"Google Safe Browsing response parsing error: {str(exc)}"
            )

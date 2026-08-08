import httpx
from typing import Optional
from app.services.threat_intel.base import ThreatIntelProvider, ProviderResult, ProviderState

class PhishTankProvider(ThreatIntelProvider):
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 2.5):
        super().__init__(name="PhishTank", enabled=True, timeout_seconds=timeout_seconds)
        self.api_key = api_key
        self.endpoint = "https://checkurl.phishtank.com/checkurl/"

    async def check_url(self, target_url: str, domain: str) -> ProviderResult:
        if not self.enabled:
            return ProviderResult(provider_name=self.name, state=ProviderState.UNAVAILABLE, error_message="Provider disabled")

        payload = {
            "url": target_url,
            "format": "json"
        }
        if self.api_key:
            payload["app_key"] = self.api_key

        headers = {
            "User-Agent": "phishtank/ApatiAspis-SecurityScanner"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.endpoint, data=payload, headers=headers)

                if response.status_code == 429:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.RATE_LIMITED,
                        error_message="PhishTank API rate limit reached"
                    )

                if response.status_code != 200:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.UNAVAILABLE,
                        error_message=f"PhishTank HTTP status {response.status_code}"
                    )

                data = response.json()
                results = data.get("results", {})
                
                # Check for in_database match
                if isinstance(results, dict):
                    in_db = results.get("in_database", False)
                    valid = results.get("valid", False)
                    phish_id = results.get("phish_id")
                    
                    if in_db and valid:
                        return ProviderResult(
                            provider_name=self.name,
                            state=ProviderState.MATCH,
                            threat_type="phishing",
                            details={
                                "phish_id": phish_id,
                                "verified": results.get("verified", False),
                                "phish_detail_page": results.get("phish_detail_page")
                            },
                            raw_response=data
                        )
                    else:
                        return ProviderResult(
                            provider_name=self.name,
                            state=ProviderState.NO_MATCH,
                            details={"in_database": False},
                            raw_response=data
                        )

                return ProviderResult(
                    provider_name=self.name,
                    state=ProviderState.NO_MATCH,
                    details={"in_database": False}
                )

        except httpx.TimeoutException:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="PhishTank query timed out"
            )
        except httpx.RequestError as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message=f"PhishTank connection error: {str(exc)}"
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.ERROR,
                error_message=f"PhishTank response parsing error: {str(exc)}"
            )

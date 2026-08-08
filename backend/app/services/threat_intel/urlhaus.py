import httpx
from typing import Optional
from app.services.threat_intel.base import ThreatIntelProvider, ProviderResult, ProviderState

class URLhausProvider(ThreatIntelProvider):
    def __init__(self, auth_key: Optional[str] = None, timeout_seconds: float = 2.5):
        super().__init__(name="URLhaus", enabled=True, timeout_seconds=timeout_seconds)
        self.auth_key = auth_key
        self.endpoint = "https://urlhaus-api.abuse.ch/v1/url/"

    async def check_url(self, target_url: str, domain: str) -> ProviderResult:
        if not self.enabled:
            return ProviderResult(provider_name=self.name, state=ProviderState.UNAVAILABLE, error_message="Provider disabled")

        payload = {
            "url": target_url
        }

        headers = {
            "User-Agent": "ApatiAspis-SecurityScanner/1.0"
        }
        if self.auth_key:
            headers["Auth-Key"] = self.auth_key

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.endpoint, data=payload, headers=headers)

                if response.status_code == 429:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.RATE_LIMITED,
                        error_message="URLhaus API rate limit reached"
                    )

                if response.status_code != 200:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.UNAVAILABLE,
                        error_message=f"URLhaus HTTP status {response.status_code}"
                    )

                data = response.json()
                query_status = data.get("query_status")

                if query_status == "ok":
                    url_status = data.get("url_status", "unknown")
                    threat = data.get("threat", "malware_download")
                    tags = data.get("tags", [])
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.MATCH,
                        threat_type=threat,
                        details={
                            "url_status": url_status,
                            "threat": threat,
                            "tags": tags,
                            "reporter": data.get("reporter"),
                            "urlhaus_reference": data.get("urlhaus_reference")
                        },
                        raw_response=data
                    )
                elif query_status == "no_results":
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.NO_MATCH,
                        details={"query_status": "no_results"},
                        raw_response=data
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.NO_MATCH,
                        details={"query_status": query_status},
                        raw_response=data
                    )

        except httpx.TimeoutException:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="URLhaus query timed out"
            )
        except httpx.RequestError as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message=f"URLhaus connection error: {str(exc)}"
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.ERROR,
                error_message=f"URLhaus response parsing error: {str(exc)}"
            )

import base64
import httpx
from typing import Optional
from app.services.threat_intel.base import ThreatIntelProvider, ProviderResult, ProviderState

class VirusTotalProvider(ThreatIntelProvider):
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 3.0):
        # VirusTotal is optional; enabled ONLY if an API key is explicitly configured
        enabled = bool(api_key and api_key.strip())
        super().__init__(name="VirusTotal", enabled=enabled, timeout_seconds=timeout_seconds)
        self.api_key = api_key.strip() if api_key else ""

    def encode_url_id(self, target_url: str) -> str:
        """Helper to base64url-encode URL string without padding for VirusTotal v3 API."""
        encoded = base64.urlsafe_b64encode(target_url.encode("utf-8")).decode("utf-8")
        return encoded.rstrip("=")

    async def check_url(self, target_url: str, domain: str) -> ProviderResult:
        if not self.enabled or not self.api_key:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="VirusTotal API key not configured (Optional provider disabled)"
            )

        url_id = self.encode_url_id(target_url)
        endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"

        headers = {
            "x-apikey": self.api_key,
            "User-Agent": "ApatiAspis-SecurityScanner/1.0"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(endpoint, headers=headers)

                if response.status_code == 404:
                    # URL not found in VirusTotal dataset
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.NO_MATCH,
                        details={"status": "not_found"}
                    )

                if response.status_code == 429:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.RATE_LIMITED,
                        error_message="VirusTotal rate limit exceeded"
                    )

                if response.status_code != 200:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.UNAVAILABLE,
                        error_message=f"VirusTotal HTTP status {response.status_code}"
                    )

                data = response.json()
                stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)
                harmless = stats.get("harmless", 0)
                undetected = stats.get("undetected", 0)

                total_flagged = malicious + suspicious

                if total_flagged > 0:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.MATCH,
                        threat_type="malicious_url" if malicious > 0 else "suspicious_url",
                        details={
                            "malicious": malicious,
                            "suspicious": suspicious,
                            "harmless": harmless,
                            "undetected": undetected
                        },
                        raw_response=data
                    )
                else:
                    return ProviderResult(
                        provider_name=self.name,
                        state=ProviderState.NO_MATCH,
                        details={
                            "malicious": 0,
                            "suspicious": 0,
                            "harmless": harmless,
                            "undetected": undetected
                        },
                        raw_response=data
                    )

        except httpx.TimeoutException:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message="VirusTotal query timed out"
            )
        except httpx.RequestError as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.UNAVAILABLE,
                error_message=f"VirusTotal connection error: {str(exc)}"
            )
        except Exception as exc:
            return ProviderResult(
                provider_name=self.name,
                state=ProviderState.ERROR,
                error_message=f"VirusTotal response parsing error: {str(exc)}"
            )

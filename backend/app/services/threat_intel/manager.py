import asyncio
import time
from typing import Dict, Any, List, Tuple
from app.config import settings
from app.services.threat_intel.base import ThreatIntelProvider, ProviderResult, ProviderState
from app.services.threat_intel.safe_browsing import GoogleSafeBrowsingProvider
from app.services.threat_intel.urlhaus import URLhausProvider
from app.services.threat_intel.virustotal import VirusTotalProvider

CACHE_TTL_SECONDS = 300  # 5 minutes cache TTL

class ThreatIntelManager:
    def __init__(self):
        self.providers: List[ThreatIntelProvider] = [
            GoogleSafeBrowsingProvider(api_key=settings.GOOGLE_SAFE_BROWSING_API_KEY),
            URLhausProvider(auth_key=settings.URLHAUS_AUTH_KEY),
            VirusTotalProvider(api_key=settings.VIRUSTOTAL_API_KEY)
        ]
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    async def query_all(self, target_url: str, domain: str) -> Dict[str, Any]:
        """
        Queries all enabled threat intelligence providers concurrently.
        Returns aggregated evidence dictionary.
        """
        now = time.time()
        if target_url in self._cache:
            timestamp, cached_result = self._cache[target_url]
            if now - timestamp < CACHE_TTL_SECONDS:
                return cached_result

        tasks = [provider.check_url(target_url, domain) for provider in self.providers]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        results_dict: Dict[str, Any] = {}
        has_match = False
        match_providers: List[str] = []

        for provider, res in zip(self.providers, raw_results):
            if isinstance(res, Exception):
                provider_res = ProviderResult(
                    provider_name=provider.name,
                    state=ProviderState.ERROR,
                    error_message=str(res)
                )
            elif isinstance(res, ProviderResult):
                provider_res = res
            else:
                provider_res = ProviderResult(
                    provider_name=provider.name,
                    state=ProviderState.ERROR,
                    error_message="Unknown provider response type"
                )

            results_dict[provider_res.provider_name] = provider_res.to_dict()

            if provider_res.state == ProviderState.MATCH:
                has_match = True
                match_providers.append(provider_res.provider_name)

        summary = {
            "has_match": has_match,
            "match_providers": match_providers,
            "providers": results_dict
        }

        self._cache[target_url] = (now, summary)
        return summary

threat_intel_manager = ThreatIntelManager()

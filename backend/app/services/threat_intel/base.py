from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional

class ProviderState(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
    RATE_LIMITED = "RATE_LIMITED"

class ProviderResult:
    def __init__(
        self,
        provider_name: str,
        state: ProviderState,
        details: Optional[Dict[str, Any]] = None,
        threat_type: Optional[str] = None,
        error_message: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ):
        self.provider_name = provider_name
        self.state = state
        self.details = details or {}
        self.threat_type = threat_type
        self.error_message = error_message
        self.raw_response = raw_response or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "state": self.state.value if isinstance(self.state, ProviderState) else str(self.state),
            "threat_type": self.threat_type,
            "error_message": self.error_message,
            "details": self.details
        }

class ThreatIntelProvider(ABC):
    def __init__(self, name: str, enabled: bool = True, timeout_seconds: float = 2.0):
        self.name = name
        self.enabled = enabled
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def check_url(self, target_url: str, domain: str) -> ProviderResult:
        """
        Checks target URL against threat intelligence dataset.
        Must never raise uncaught exceptions; return ProviderResult with appropriate state.
        """
        pass

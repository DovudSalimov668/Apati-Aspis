from typing import Dict, Any, List, Optional
from app.analysis.normalizer import NormalizedURL
from app.analysis.ssrf import SSRFCheckResult
from app.analysis.heuristics import HeuristicResult

class RiskAssessment:
    def __init__(self, score: int, level: str, confidence: str, reasons: List[str]):
        self.score = min(100, max(0, score))
        self.level = level
        self.confidence = confidence
        self.reasons = reasons

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "level": self.level,
            "confidence": self.confidence,
            "reasons": self.reasons
        }

def determine_risk_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MODERATE"
    else:
        return "LOW"

def calculate_risk(
    normalization: NormalizedURL,
    ssrf_check: SSRFCheckResult,
    heuristics: List[HeuristicResult],
    threat_intel: Dict[str, Any]
) -> RiskAssessment:
    """
    Deterministic risk calculation engine.
    - Risk score: 0 to 100 based on SSRF, threat intel, and heuristic evidence.
    - Risk level: LOW (0-24), MODERATE (25-49), HIGH (50-74), CRITICAL (75-100).
    - Confidence: HIGH, MEDIUM, LOW based on threat intel provider availability.
    """
    reasons: List[str] = []

    # 1. Invalid URL Handling
    if not normalization.is_valid:
        return RiskAssessment(
            score=100,
            level="CRITICAL",
            confidence="HIGH",
            reasons=[f"Invalid URL structure: {normalization.error_message}"]
        )

    # 2. SSRF Blocked Handling
    if not ssrf_check.is_safe:
        return RiskAssessment(
            score=100,
            level="CRITICAL",
            confidence="HIGH",
            reasons=[f"Blocked by SSRF Protection: {ssrf_check.blocked_reason}"]
        )

    score = 0
    confidence = "HIGH"

    # 3. Threat Intelligence Evidence
    has_match = threat_intel.get("has_match", False)
    match_providers = threat_intel.get("match_providers", [])
    providers_dict = threat_intel.get("providers", {})

    if has_match:
        matched_str = ", ".join(match_providers)
        reasons.append(f"THREAT MATCH: Indicator detected in threat intelligence database ({matched_str}).")
        score = max(score, 90)

    # 4. Heuristics Evidence
    heuristic_score_sum = 0
    for sig in heuristics:
        reasons.append(sig.message)
        heuristic_score_sum += sig.score_impact

    score = min(100, score + heuristic_score_sum)

    # 5. Provider Availability & Confidence Evaluation
    # Provider failures degrade confidence, NOT score.
    unavailable_count = 0
    total_primary_providers = 0

    for pname in ["PhishTank", "URLhaus"]:
        if pname in providers_dict:
            total_primary_providers += 1
            pstate = providers_dict[pname].get("state")
            if pstate in ("UNAVAILABLE", "ERROR", "RATE_LIMITED"):
                unavailable_count += 1

    if unavailable_count == total_primary_providers and total_primary_providers > 0:
        confidence = "LOW"
        reasons.append("Confidence degraded: Primary threat intelligence providers were unavailable.")
    elif unavailable_count > 0:
        confidence = "MEDIUM"
        reasons.append("Confidence slightly degraded: One or more threat intelligence providers timed out or rate-limited.")

    if not reasons:
        reasons.append("No obvious URL risk signals detected.")

    level = determine_risk_level(score)

    return RiskAssessment(
        score=score,
        level=level,
        confidence=confidence,
        reasons=reasons
    )

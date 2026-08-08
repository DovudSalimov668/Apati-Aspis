import re
from typing import Dict, Any, List, Tuple
from app.analysis.normalizer import NormalizedURL

SUSPICIOUS_KEYWORDS = {
    "login", "signin", "verify", "verification", "account", "banking", "update", "secure",
    "wallet", "credential", "auth", "confirm", "billing", "paypal", "apple", "google", "microsoft",
    "netflix", "amazon", "support", "security", "passcode"
}

SUSPICIOUS_EXTENSIONS = {".exe", ".zip", ".scr", ".bat", ".vbs", ".cmd", ".ps1", ".apk"}

SUSPICIOUS_TLDS = {".top", ".xyz", ".work", ".click", ".gq", ".cf", ".ml", ".tk", ".ga", ".fit", ".icu", ".cam"}

SUSPICIOUS_QUERY_KEYS = {"token", "auth", "password", "pass", "key", "secret", "cmd", "exec", "redirect"}

class HeuristicResult:
    def __init__(self, code: str, severity: str, message: str, score_impact: int):
        self.code = code
        self.severity = severity  # 'LOW', 'MEDIUM', 'HIGH'
        self.message = message
        self.score_impact = score_impact

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "score_impact": self.score_impact
        }


def evaluate_heuristics(normalized: NormalizedURL) -> Tuple[List[HeuristicResult], int]:
    """
    Evaluates heuristic risk signals from a normalized URL.
    Returns (signals_list, total_heuristic_score).
    """
    signals: List[HeuristicResult] = []
    score = 0

    if not normalized.is_valid:
        return signals, 0

    # 1. IP-based URL
    if normalized.is_ip:
        sig = HeuristicResult(
            code="IP_BASED_URL",
            severity="MEDIUM",
            message=f"URL uses a direct IP address ('{normalized.hostname}') instead of a domain name.",
            score_impact=25
        )
        signals.append(sig)
        score += sig.score_impact

    # 2. Punycode / IDN Domain
    if normalized.is_punycode:
        sig = HeuristicResult(
            code="PUNYCODE_DOMAIN",
            severity="MEDIUM",
            message=f"Domain contains Punycode encoding ('{normalized.ascii_hostname}'), often used for homograph phishing.",
            score_impact=20
        )
        signals.append(sig)
        score += sig.score_impact

    # 3. Excessive Subdomains
    if not normalized.is_ip and normalized.ascii_hostname:
        domain_parts = [p for p in normalized.ascii_hostname.split('.') if p]
        if len(domain_parts) > 4:
            sig = HeuristicResult(
                code="EXCESSIVE_SUBDOMAINS",
                severity="MEDIUM",
                message=f"URL contains an unusually high number of subdomains ({len(domain_parts) - 2} subdomains).",
                score_impact=15
            )
            signals.append(sig)
            score += sig.score_impact

    # 4. Suspicious TLD
    if not normalized.is_ip and normalized.ascii_hostname:
        domain_parts = normalized.ascii_hostname.split('.')
        if len(domain_parts) >= 2:
            tld = f".{domain_parts[-1]}".lower()
            if tld in SUSPICIOUS_TLDS:
                sig = HeuristicResult(
                    code="SUSPICIOUS_TLD",
                    severity="LOW",
                    message=f"Domain uses top-level domain '{tld}' frequently observed in scam campaigns.",
                    score_impact=10
                )
                signals.append(sig)
                score += sig.score_impact

    # 5. Suspicious Non-Standard Port
    if normalized.port and normalized.port not in (80, 443):
        sig = HeuristicResult(
            code="SUSPICIOUS_PORT",
            severity="MEDIUM",
            message=f"URL uses non-standard web port {normalized.port}.",
            score_impact=15
        )
        signals.append(sig)
        score += sig.score_impact

    # 6. Excessive URL Length
    raw_length = len(normalized.raw_url)
    if raw_length > 120:
        sig = HeuristicResult(
            code="EXCESSIVE_URL_LENGTH",
            severity="LOW",
            message=f"URL is unusually long ({raw_length} characters).",
            score_impact=10
        )
        signals.append(sig)
        score += sig.score_impact

    # 7. Suspicious Path & Extensions
    path_lower = normalized.path.lower()
    found_path_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in path_lower]
    if found_path_keywords:
        sig = HeuristicResult(
            code="SUSPICIOUS_PATH_KEYWORDS",
            severity="LOW",
            message=f"URL path contains sensitive keywords ({', '.join(found_path_keywords[:3])}).",
            score_impact=10
        )
        signals.append(sig)
        score += sig.score_impact

    found_ext = [ext for ext in SUSPICIOUS_EXTENSIONS if path_lower.endswith(ext)]
    if found_ext:
        sig = HeuristicResult(
            code="SUSPICIOUS_FILE_EXTENSION",
            severity="HIGH",
            message=f"URL targets an executable/archive file extension ({found_ext[0]}).",
            score_impact=30
        )
        signals.append(sig)
        score += sig.score_impact

    # 8. Suspicious Query Parameters
    if normalized.query:
        query_lower = normalized.query.lower()
        found_query_keys = [key for key in SUSPICIOUS_QUERY_KEYS if key in query_lower]
        if found_query_keys:
            sig = HeuristicResult(
                code="SUSPICIOUS_QUERY_PARAMS",
                severity="MEDIUM",
                message=f"URL query parameters contain sensitive authentication keys ({', '.join(found_query_keys[:3])}).",
                score_impact=15
            )
            signals.append(sig)
            score += sig.score_impact

    # 9. Suspicious Structure (@ symbol, double slashes in path)
    if "@" in normalized.raw_url:
        sig = HeuristicResult(
            code="SUSPICIOUS_USERINFO_AT_SYMBOL",
            severity="HIGH",
            message="URL contains '@' character which can obscure the real destination host.",
            score_impact=30
        )
        signals.append(sig)
        score += sig.score_impact

    # Cap score at 100
    score = min(100, score)

    return signals, score

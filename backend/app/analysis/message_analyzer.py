import re
from typing import List, Tuple, Dict, Any
from app.analysis.normalizer import normalize_url
from app.analysis.heuristics import HeuristicResult

# Regular expression for extracting http/https or www URLs from text
URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+', re.IGNORECASE)

# Category keywords for social engineering message detection
URGENCY_KEYWORDS = {
    "immediately", "urgent", "action required", "within 24 hours", "suspended", "account locked",
    "unauthorized access", "compromised", "security alert", "critical notice", "expire"
}

CREDENTIAL_KEYWORDS = {
    "verify password", "login now", "update security", "confirm account", "enter passcode",
    "validate identity", "reset password", "security verification"
}

PAYMENT_KEYWORDS = {
    "wire money", "gift card", "crypto", "unpaid invoice", "bitcoin", "payment required",
    "claim refund", "direct deposit", "overdue fee"
}

BRAND_KEYWORDS = {
    "paypal", "apple", "google", "microsoft", "netflix", "amazon", "usps", "fedex", "dhl",
    "bank of america", "chase", "wells fargo", "irs", "geek squad"
}

def extract_urls_from_text(text: str) -> List[str]:
    """Extracts all embedded HTTP/HTTPS/WWW URLs from raw text."""
    if not text or not isinstance(text, str):
        return []
    matches = URL_REGEX.findall(text)
    cleaned_urls = []
    for match in matches:
        # Strip trailing punctuation commonly attached to URLs in text
        url = match.rstrip(".,;!?)']}\"")
        if url and url not in cleaned_urls:
            cleaned_urls.append(url)
    return cleaned_urls


def evaluate_message_heuristics(text: str) -> Tuple[List[HeuristicResult], int]:
    """
    Evaluates social engineering language heuristics on message content.
    Returns (list_of_heuristic_signals, total_impact_score).
    """
    signals: List[HeuristicResult] = []
    score = 0
    if not text or not isinstance(text, str):
        return signals, 0

    text_lower = text.lower()

    # 1. Urgency / Pressure Tactics
    found_urgency = [kw for kw in URGENCY_KEYWORDS if kw in text_lower]
    if found_urgency:
        sig = HeuristicResult(
            code="MESSAGE_URGENCY_PRESSURE",
            severity="MEDIUM",
            message=f"Message uses urgent/coercive language ('{found_urgency[0]}').",
            score_impact=20
        )
        signals.append(sig)
        score += sig.score_impact

    # 2. Credential Harvesting Requests
    found_cred = [kw for kw in CREDENTIAL_KEYWORDS if kw in text_lower]
    if found_cred:
        sig = HeuristicResult(
            code="MESSAGE_CREDENTIAL_REQUEST",
            severity="HIGH",
            message=f"Message prompts user for sensitive login credentials ('{found_cred[0]}').",
            score_impact=30
        )
        signals.append(sig)
        score += sig.score_impact

    # 3. Payment / Financial Demands
    found_pay = [kw for kw in PAYMENT_KEYWORDS if kw in text_lower]
    if found_pay:
        sig = HeuristicResult(
            code="MESSAGE_PAYMENT_DEMAND",
            severity="HIGH",
            message=f"Message contains financial/payment demands ('{found_pay[0]}').",
            score_impact=30
        )
        signals.append(sig)
        score += sig.score_impact

    # 4. Brand Impersonation Signals
    found_brand = [kw for kw in BRAND_KEYWORDS if kw in text_lower]
    if found_brand:
        sig = HeuristicResult(
            code="MESSAGE_BRAND_IMPERSONATION",
            severity="MEDIUM",
            message=f"Message references major brand ('{found_brand[0]}'), potential impersonation attempt.",
            score_impact=15
        )
        signals.append(sig)
        score += sig.score_impact

    # 5. Embedded Links in Text
    extracted_urls = extract_urls_from_text(text)
    if extracted_urls:
        sig = HeuristicResult(
            code="MESSAGE_EMBEDDED_LINKS",
            severity="LOW",
            message=f"Message contains {len(extracted_urls)} embedded link(s).",
            score_impact=10
        )
        signals.append(sig)
        score += sig.score_impact

    score = min(100, score)
    return signals, score

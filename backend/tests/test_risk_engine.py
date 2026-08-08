from app.analysis.normalizer import normalize_url
from app.analysis.ssrf import validate_ssrf, SSRFCheckResult
from app.analysis.heuristics import HeuristicResult
from app.analysis.risk_engine import calculate_risk, determine_risk_level

def test_risk_level_boundaries():
    assert determine_risk_level(0) == "LOW"
    assert determine_risk_level(24) == "LOW"
    assert determine_risk_level(25) == "MODERATE"
    assert determine_risk_level(49) == "MODERATE"
    assert determine_risk_level(50) == "HIGH"
    assert determine_risk_level(74) == "HIGH"
    assert determine_risk_level(75) == "CRITICAL"
    assert determine_risk_level(100) == "CRITICAL"

def test_no_signals():
    norm = normalize_url("https://example.com")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="example.com")
    threat_intel = {"has_match": False, "providers": {"PhishTank": {"state": "NO_MATCH"}, "URLhaus": {"state": "NO_MATCH"}}}

    res = calculate_risk(norm, ssrf, [], threat_intel)
    assert res.score == 0
    assert res.level == "LOW"
    assert res.confidence == "HIGH"

def test_weak_signal():
    norm = normalize_url("http://example.top")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="example.top")
    heuristics = [HeuristicResult("SUSPICIOUS_TLD", "LOW", "Suspicious TLD .top", 10)]
    threat_intel = {"has_match": False, "providers": {"PhishTank": {"state": "NO_MATCH"}, "URLhaus": {"state": "NO_MATCH"}}}

    res = calculate_risk(norm, ssrf, heuristics, threat_intel)
    assert res.score == 10
    assert res.level == "LOW"

def test_multiple_signals():
    norm = normalize_url("http://a.b.c.d.e.example.top:8080/")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="example.top")
    heuristics = [
        HeuristicResult("EXCESSIVE_SUBDOMAINS", "MEDIUM", "Subdomains", 15),
        HeuristicResult("SUSPICIOUS_TLD", "LOW", "TLD", 10),
        HeuristicResult("SUSPICIOUS_PORT", "MEDIUM", "Port", 15)
    ]
    threat_intel = {"has_match": False, "providers": {"PhishTank": {"state": "NO_MATCH"}, "URLhaus": {"state": "NO_MATCH"}}}

    res = calculate_risk(norm, ssrf, heuristics, threat_intel)
    assert res.score == 40
    assert res.level == "MODERATE"

def test_strong_signal():
    norm = normalize_url("http://google.com@malicious-site.com/payload.exe")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="malicious-site.com")
    heuristics = [
        HeuristicResult("SUSPICIOUS_USERINFO_AT_SYMBOL", "HIGH", "@ symbol", 30),
        HeuristicResult("SUSPICIOUS_FILE_EXTENSION", "HIGH", ".exe file", 30)
    ]
    threat_intel = {"has_match": False, "providers": {"PhishTank": {"state": "NO_MATCH"}, "URLhaus": {"state": "NO_MATCH"}}}

    res = calculate_risk(norm, ssrf, heuristics, threat_intel)
    assert res.score == 60
    assert res.level == "HIGH"

def test_threat_intelligence_match():
    norm = normalize_url("http://phishing.example.com")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="phishing.example.com")
    threat_intel = {
        "has_match": True,
        "match_providers": ["PhishTank"],
        "providers": {"PhishTank": {"state": "MATCH"}, "URLhaus": {"state": "NO_MATCH"}}
    }

    res = calculate_risk(norm, ssrf, [], threat_intel)
    assert res.score >= 90
    assert res.level == "CRITICAL"
    assert res.confidence == "HIGH"
    assert "THREAT MATCH" in res.reasons[0]

def test_unavailable_provider_degrades_confidence_not_score():
    norm = normalize_url("https://example.com")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="example.com")
    threat_intel = {
        "has_match": False,
        "providers": {"PhishTank": {"state": "UNAVAILABLE"}, "URLhaus": {"state": "NO_MATCH"}}
    }

    res = calculate_risk(norm, ssrf, [], threat_intel)
    # Unavailable provider must NOT force score to malicious or safe arbitrarily
    assert res.score == 0
    assert res.level == "LOW"
    # Confidence is degraded to MEDIUM due to provider unavailability
    assert res.confidence == "MEDIUM"
    assert "Confidence slightly degraded" in res.reasons[-1]

def test_all_providers_unavailable():
    norm = normalize_url("https://example.com")
    ssrf = SSRFCheckResult(is_safe=True, resolved_ips=["93.184.216.34"], hostname="example.com")
    threat_intel = {
        "has_match": False,
        "providers": {"PhishTank": {"state": "UNAVAILABLE"}, "URLhaus": {"state": "UNAVAILABLE"}}
    }

    res = calculate_risk(norm, ssrf, [], threat_intel)
    assert res.score == 0
    assert res.confidence == "LOW"
    assert "Primary threat intelligence providers were unavailable" in res.reasons[-1]

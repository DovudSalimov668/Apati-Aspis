from app.analysis.normalizer import normalize_url
from app.analysis.heuristics import evaluate_heuristics

def test_ip_based_url_heuristic():
    norm = normalize_url("http://93.184.216.34/login")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "IP_BASED_URL" in codes
    assert score >= 25

def test_punycode_domain_heuristic():
    norm = normalize_url("http://xn--e1afmkfd.xn--p1ai/")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "PUNYCODE_DOMAIN" in codes

def test_excessive_subdomains_heuristic():
    norm = normalize_url("http://a.b.c.d.e.example.com/")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "EXCESSIVE_SUBDOMAINS" in codes

def test_suspicious_port_heuristic():
    norm = normalize_url("https://example.com:8443/")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "SUSPICIOUS_PORT" in codes

def test_executable_extension_heuristic():
    norm = normalize_url("http://example.com/payload.exe")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "SUSPICIOUS_FILE_EXTENSION" in codes

def test_at_symbol_obscuration_heuristic():
    norm = normalize_url("http://google.com@phishing-site.com/")
    signals, score = evaluate_heuristics(norm)
    codes = [s.code for s in signals]
    assert "SUSPICIOUS_USERINFO_AT_SYMBOL" in codes

from app.analysis.normalizer import normalize_url

def test_valid_http_url():
    norm = normalize_url("http://example.com")
    assert norm.is_valid is True
    assert norm.scheme == "http"
    assert norm.hostname == "example.com"
    assert norm.normalized_url == "http://example.com/"

def test_url_with_custom_port():
    norm = normalize_url("https://example.com:8443/api/v1")
    assert norm.is_valid is True
    assert norm.port == 8443
    assert norm.normalized_url == "https://example.com:8443/api/v1"

def test_default_port_omission():
    norm = normalize_url("http://example.com:80/page")
    assert norm.is_valid is True
    assert norm.port is None
    assert norm.normalized_url == "http://example.com/page"

def test_punycode_idn_normalization():
    norm = normalize_url("http://xn--e1afmkfd.xn--p1ai/")
    assert norm.is_valid is True
    assert norm.is_punycode is True
    assert "xn--" in norm.ascii_hostname

def test_ip_address_url():
    norm = normalize_url("http://192.168.1.1:8080/admin")
    assert norm.is_valid is True
    assert norm.is_ip is True
    assert norm.hostname == "192.168.1.1"

def test_malformed_scheme():
    norm = normalize_url("ftp://files.example.com")
    assert norm.is_valid is False
    assert "Unsupported URL scheme" in norm.error_message

def test_empty_url():
    norm = normalize_url("")
    assert norm.is_valid is False

def test_query_string_canonicalization():
    norm = normalize_url("https://example.com/search?b=2&a=1")
    assert norm.is_valid is True
    assert norm.query == "a=1&b=2"
    assert norm.normalized_url == "https://example.com/search?a=1&b=2"

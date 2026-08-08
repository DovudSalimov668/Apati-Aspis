from app.analysis.ssrf import validate_ssrf

def test_block_localhost_string():
    res = validate_ssrf("localhost")
    assert res.is_safe is False
    assert "Blocked internal hostname" in res.blocked_reason

def test_block_loopback_ipv4():
    res = validate_ssrf("127.0.0.1")
    assert res.is_safe is False
    assert "prohibited IP space" in res.blocked_reason

def test_block_private_10_network():
    res = validate_ssrf("10.0.0.1")
    assert res.is_safe is False

def test_block_private_172_network():
    res = validate_ssrf("172.16.0.5")
    assert res.is_safe is False

def test_block_private_192_network():
    res = validate_ssrf("192.168.1.1")
    assert res.is_safe is False

def test_block_aws_metadata_ip():
    res = validate_ssrf("169.254.169.254")
    assert res.is_safe is False

def test_block_ipv6_loopback():
    res = validate_ssrf("::1")
    assert res.is_safe is False

def test_block_ipv6_unique_local():
    res = validate_ssrf("fc00::1")
    assert res.is_safe is False

def test_block_ipv6_link_local():
    res = validate_ssrf("fe80::1")
    assert res.is_safe is False

def test_allow_public_ip():
    # 8.8.8.8 (Google Public DNS)
    res = validate_ssrf("8.8.8.8")
    assert res.is_safe is True
    assert "8.8.8.8" in res.resolved_ips

import socket
import ipaddress
from typing import List, Tuple, Dict, Any, Optional

# Prohibited IPv4 and IPv6 Networks
PROHIBITED_NETWORKS = [
    # IPv4 Loopback
    ipaddress.ip_network("127.0.0.0/8"),
    # IPv4 Private
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    # IPv4 Link-local / Cloud Metadata (e.g. AWS 169.254.169.254)
    ipaddress.ip_network("169.254.0.0/16"),
    # Current network
    ipaddress.ip_network("0.0.0.0/8"),
    # Carrier-grade NAT
    ipaddress.ip_network("100.64.0.0/10"),
    # Documentation & Testing IPv4
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    # Broadcast / Reserved
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),

    # IPv6 Loopback
    ipaddress.ip_network("::1/128"),
    # IPv6 Unspecified
    ipaddress.ip_network("::/128"),
    # IPv6 Unique Local (Private)
    ipaddress.ip_network("fc00::/7"),
    # IPv6 Link-local
    ipaddress.ip_network("fe80::/10"),
    # IPv6 Documentation
    ipaddress.ip_network("2001:db8::/32"),
]

# Explicit localhost names
BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "localhost.local",
    "broadcasthost",
    "local",
}

class SSRFCheckResult:
    def __init__(
        self,
        is_safe: bool,
        blocked_reason: Optional[str] = None,
        resolved_ips: Optional[List[str]] = None,
        hostname: str = ""
    ):
        self.is_safe = is_safe
        self.blocked_reason = blocked_reason
        self.resolved_ips = resolved_ips or []
        self.hostname = hostname

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "blocked_reason": self.blocked_reason,
            "resolved_ips": self.resolved_ips,
            "hostname": self.hostname
        }


def is_ip_prohibited(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks if an IP address belongs to any private, loopback, or restricted range."""
    # Check built-in properties
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True

    # Handle IPv4-mapped IPv6 addresses (e.g. ::ffff:127.0.0.1)
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        return is_ip_prohibited(ip.ipv4_mapped)

    # Check against explicitly configured prohibited CIDR blocks
    for network in PROHIBITED_NETWORKS:
        if ip.version == network.version and ip in network:
            return True

    return False


def resolve_hostname_ips(hostname: str, port: int = 80) -> List[str]:
    """Safely resolves all A and AAAA records for a hostname."""
    resolved_ips: List[str] = []
    
    # If hostname is already an IP address string
    clean_host = hostname.strip("[]")
    try:
        ip_obj = ipaddress.ip_address(clean_host)
        return [str(ip_obj)]
    except ValueError:
        pass

    try:
        # Resolve address info using standard socket library
        addr_info = socket.getaddrinfo(clean_host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for item in addr_info:
            ip_str = item[4][0]
            if ip_str not in resolved_ips:
                resolved_ips.append(ip_str)
    except socket.gaierror:
        pass
    except Exception:
        pass

    return resolved_ips


def validate_ssrf(hostname: str, port: int = 80) -> SSRFCheckResult:
    """
    Validates a target hostname/IP against SSRF risks.
    1. Checks explicit localhost hostnames.
    2. Resolves DNS records.
    3. Checks every resolved IP against prohibited IP space.
    """
    if not hostname or not isinstance(hostname, str):
        return SSRFCheckResult(is_safe=False, blocked_reason="Invalid hostname provided", hostname=str(hostname))

    clean_host = hostname.strip("[]").lower()

    # Block explicit localhost hostnames
    if clean_host in BLOCKED_HOSTNAMES or clean_host.endswith(".local") or clean_host.endswith(".localhost"):
        return SSRFCheckResult(
            is_safe=False,
            blocked_reason=f"Blocked internal hostname '{hostname}'",
            hostname=hostname
        )

    # Resolve IP addresses
    resolved_ips = resolve_hostname_ips(clean_host, port)

    if not resolved_ips:
        # If DNS resolution yields no IPs, treat as unsafe/unresolvable for probing
        return SSRFCheckResult(
            is_safe=False,
            blocked_reason=f"Unable to resolve DNS for host '{hostname}'",
            hostname=hostname,
            resolved_ips=[]
        )

    # Validate every resolved IP
    for ip_str in resolved_ips:
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if is_ip_prohibited(ip_obj):
                return SSRFCheckResult(
                    is_safe=False,
                    blocked_reason=f"Host '{hostname}' resolved to prohibited IP space ({ip_str})",
                    resolved_ips=resolved_ips,
                    hostname=hostname
                )
        except ValueError:
            return SSRFCheckResult(
                is_safe=False,
                blocked_reason=f"Invalid IP address format resolved: '{ip_str}'",
                resolved_ips=resolved_ips,
                hostname=hostname
            )

    # All resolved IPs are public and safe
    return SSRFCheckResult(
        is_safe=True,
        resolved_ips=resolved_ips,
        hostname=hostname
    )

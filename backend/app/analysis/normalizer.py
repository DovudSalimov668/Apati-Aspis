import re
import ipaddress
import idna
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, unquote
from typing import Dict, Any, Optional

class NormalizedURL:
    def __init__(
        self,
        raw_url: str,
        is_valid: bool,
        error_message: Optional[str] = None,
        scheme: str = "",
        hostname: str = "",
        ascii_hostname: str = "",
        port: Optional[int] = None,
        path: str = "/",
        query: str = "",
        fragment: str = "",
        normalized_url: str = "",
        is_ip: bool = False,
        ip_version: Optional[int] = None,
        is_punycode: bool = False
    ):
        self.raw_url = raw_url
        self.is_valid = is_valid
        self.error_message = error_message
        self.scheme = scheme
        self.hostname = hostname
        self.ascii_hostname = ascii_hostname
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment
        self.normalized_url = normalized_url
        self.is_ip = is_ip
        self.ip_version = ip_version
        self.is_punycode = is_punycode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_url": self.raw_url,
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "scheme": self.scheme,
            "hostname": self.hostname,
            "ascii_hostname": self.ascii_hostname,
            "port": self.port,
            "path": self.path,
            "query": self.query,
            "fragment": self.fragment,
            "normalized_url": self.normalized_url,
            "is_ip": self.is_ip,
            "ip_version": self.ip_version,
            "is_punycode": self.is_punycode
        }


def normalize_url(raw_url: str) -> NormalizedURL:
    if not raw_url or not isinstance(raw_url, str):
        return NormalizedURL(raw_url=str(raw_url), is_valid=False, error_message="URL must be a non-empty string")

    url_str = raw_url.strip()

    # Prepend scheme if missing (default to http for parsing)
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*://', url_str):
        url_str = "http://" + url_str

    try:
        parsed = urlparse(url_str)
    except Exception as e:
        return NormalizedURL(raw_url=raw_url, is_valid=False, error_message=f"Invalid URL structure: {str(e)}")

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        return NormalizedURL(
            raw_url=raw_url,
            is_valid=False,
            error_message=f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted."
        )

    if not parsed.netloc:
        return NormalizedURL(raw_url=raw_url, is_valid=False, error_message="Missing hostname in URL")

    # Extract hostname and port
    hostname_raw = parsed.hostname or ""
    if not hostname_raw:
        return NormalizedURL(raw_url=raw_url, is_valid=False, error_message="Invalid or missing host in URL")

    hostname_lower = hostname_raw.lower()

    # Check if host is IP address
    is_ip = False
    ip_version = None
    try:
        ip_obj = ipaddress.ip_address(hostname_lower.strip("[]"))
        is_ip = True
        ip_version = ip_obj.version
        ascii_hostname = str(ip_obj)
        hostname_clean = ascii_hostname
        is_punycode = False
    except ValueError:
        is_ip = False
        # IDN / Punycode handling
        try:
            ascii_hostname = idna.encode(hostname_lower).decode('ascii')
            hostname_clean = ascii_hostname
            is_punycode = "xn--" in ascii_hostname.lower()
        except idna.IDNAError as e:
            return NormalizedURL(
                raw_url=raw_url,
                is_valid=False,
                error_message=f"Invalid domain name encoding (IDN error): {str(e)}"
            )

    port = parsed.port
    # Omit default ports
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    # Reconstruct netloc
    if port:
        netloc = f"[{hostname_clean}]:{port}" if ":" in hostname_clean and not hostname_clean.startswith("[") else f"{hostname_clean}:{port}"
    else:
        netloc = f"[{hostname_clean}]" if ":" in hostname_clean and not hostname_clean.startswith("[") else hostname_clean

    # Path normalization
    path = parsed.path
    if not path:
        path = "/"
    else:
        # Unquote path safely
        path = unquote(path)
        # Collapse multiple slashes
        path = re.sub(r'/{2,}', '/', path)

    # Query string normalization
    query = parsed.query
    if query:
        # Parse and sort query params for canonical form
        query_pairs = parse_qsl(query, keep_blank_values=True)
        query_sorted = sorted(query_pairs)
        query = urlencode(query_sorted)

    fragment = parsed.fragment

    # Reconstruct canonical normalized URL
    normalized_str = urlunparse((scheme, netloc, path, "", query, fragment))

    return NormalizedURL(
        raw_url=raw_url,
        is_valid=True,
        scheme=scheme,
        hostname=hostname_clean,
        ascii_hostname=ascii_hostname,
        port=port,
        path=path,
        query=query,
        fragment=fragment,
        normalized_url=normalized_str,
        is_ip=is_ip,
        ip_version=ip_version,
        is_punycode=is_punycode
    )

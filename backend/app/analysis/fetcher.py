import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from app.analysis.normalizer import normalize_url, NormalizedURL
from app.analysis.ssrf import validate_ssrf, SSRFCheckResult

MAX_REDIRECTS = 5
MAX_RESPONSE_SIZE = 1 * 1024 * 1024  # 1MB limit
DEFAULT_TIMEOUT_SECONDS = 3.0

class RedirectChainItem:
    def __init__(self, url: str, status_code: int, is_ssrf_safe: bool):
        self.url = url
        self.status_code = status_code
        self.is_ssrf_safe = is_ssrf_safe

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "is_ssrf_safe": self.is_ssrf_safe
        }

class SafeFetchResult:
    def __init__(
        self,
        success: bool,
        error: Optional[str] = None,
        final_url: str = "",
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "",
        content_length: int = 0,
        redirect_chain: Optional[List[RedirectChainItem]] = None,
        ssrf_blocked: bool = False
    ):
        self.success = success
        self.error = error
        self.final_url = final_url
        self.status_code = status_code
        self.headers = headers or {}
        self.content_type = content_type
        self.content_length = content_length
        self.redirect_chain = redirect_chain or []
        self.ssrf_blocked = ssrf_blocked

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "error": self.error,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "headers": self.headers,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "redirect_chain": [item.to_dict() for item in self.redirect_chain],
            "ssrf_blocked": self.ssrf_blocked
        }


async def safe_fetch_url(
    target_url: str,
    max_redirects: int = MAX_REDIRECTS,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_body_bytes: int = MAX_RESPONSE_SIZE
) -> SafeFetchResult:
    """
    Safely probes an HTTP/HTTPS endpoint with:
    1. Pre-flight SSRF validation on initial host.
    2. Manual redirect following with SSRF validation on EVERY step in redirect chain.
    3. Strict timeouts and response size limits.
    """
    current_url = target_url
    redirect_chain: List[RedirectChainItem] = []

    timeout_config = httpx.Timeout(timeout_seconds, connect=2.0)

    async with httpx.AsyncClient(timeout=timeout_config, follow_redirects=False) as client:
        for _ in range(max_redirects + 1):
            # 1. Normalize current URL
            norm = normalize_url(current_url)
            if not norm.is_valid:
                return SafeFetchResult(
                    success=False,
                    error=f"Invalid URL in request chain: {norm.error_message}",
                    redirect_chain=redirect_chain
                )

            # 2. SSRF Pre-flight check on current target
            ssrf = validate_ssrf(norm.ascii_hostname, norm.port or (80 if norm.scheme == "http" else 443))
            if not ssrf.is_safe:
                return SafeFetchResult(
                    success=False,
                    error=f"SSRF Protection Blocked Request: {ssrf.blocked_reason}",
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    ssrf_blocked=True
                )

            # 3. Attempt HEAD/GET request safely
            try:
                # Use GET with stream to enforce max body size limit safely
                async with client.stream("GET", norm.normalized_url, headers={"User-Agent": "ApatiAspis-SecurityScanner/1.0"}) as response:
                    status_code = response.status_code
                    content_type = response.headers.get("content-type", "")
                    
                    redirect_chain.append(RedirectChainItem(url=norm.normalized_url, status_code=status_code, is_ssrf_safe=True))

                    # Check for redirect (301, 302, 303, 307, 308)
                    if status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get("location")
                        if not location:
                            return SafeFetchResult(
                                success=False,
                                error=f"Redirect HTTP {status_code} received without Location header",
                                final_url=norm.normalized_url,
                                status_code=status_code,
                                redirect_chain=redirect_chain
                            )
                        # Resolve relative redirect URLs against current URL
                        current_url = urljoin(norm.normalized_url, location)
                        continue

                    # Read body chunk up to max size limit
                    chunks = []
                    bytes_read = 0
                    async for chunk in response.aiter_bytes():
                        bytes_read += len(chunk)
                        if bytes_read > max_body_bytes:
                            return SafeFetchResult(
                                success=False,
                                error=f"Response body exceeded max size limit of {max_body_bytes} bytes",
                                final_url=norm.normalized_url,
                                status_code=status_code,
                                content_type=content_type,
                                content_length=bytes_read,
                                redirect_chain=redirect_chain
                            )
                        chunks.append(chunk)

                    headers_dict = dict(response.headers)
                    return SafeFetchResult(
                        success=True,
                        final_url=norm.normalized_url,
                        status_code=status_code,
                        headers=headers_dict,
                        content_type=content_type,
                        content_length=bytes_read,
                        redirect_chain=redirect_chain
                    )

            except httpx.TimeoutException:
                return SafeFetchResult(
                    success=False,
                    error=f"Connection timed out after {timeout_seconds} seconds",
                    final_url=current_url,
                    redirect_chain=redirect_chain
                )
            except httpx.RequestError as exc:
                return SafeFetchResult(
                    success=False,
                    error=f"Network request error: {str(exc)}",
                    final_url=current_url,
                    redirect_chain=redirect_chain
                )
            except Exception as exc:
                return SafeFetchResult(
                    success=False,
                    error=f"Unexpected fetch error: {str(exc)}",
                    final_url=current_url,
                    redirect_chain=redirect_chain
                )

        # Exceeded max redirects
        return SafeFetchResult(
            success=False,
            error=f"Exceeded maximum allowed redirects ({max_redirects})",
            final_url=current_url,
            redirect_chain=redirect_chain
        )

# APATI ASPIS — Security Guarantees & Guidelines

## 1. SSRF (Server-Side Request Forgery) Protection
APATI ASPIS resolves all target hostnames before sending external network probes. Any request resolving to private, loopback, link-local, or cloud metadata IP address space is immediately blocked.

Blocked Ranges include:
- `127.0.0.0/8` (Loopback)
- `10.0.0.0/8` (Private network)
- `172.16.0.0/12` (Private network)
- `192.168.0.0/16` (Private network)
- `169.254.0.0/16` (Link-local / AWS metadata `169.254.169.254`)
- `::1` (IPv6 Loopback)
- `fc00::/7` (IPv6 Unique Local)
- `fe80::/10` (IPv6 Link-local)

## 2. Password Safety (k-Anonymity)
When checking password breach status:
- Passwords are SHA-1 hashed locally.
- Only the first 5 characters (prefix) of the SHA-1 hash are sent to HIBP.
- Plaintext passwords are never written to disk, sent to external AI services, or logged in application logs.

## 3. Threat Intelligence Fallbacks
External API timeouts or provider unavailability (e.g. PhishTank, URLhaus) will degrade gracefully. Provider errors reduce decision confidence but will never result in an arbitrary "SAFE" declaration.

## 4. Prompt Injection Resistance
All user-submitted content (URLs, SMS text, OCR output, QR payload) is marked as UNTRUSTED DATA when supplied to Gemini API models. Strict prompt demarcation prevents adversarial instructions from hijacking the explanation model.

# APATI ASPIS — Threat Intelligence Architecture

## Primary Threat Intelligence Providers
1. **PhishTank**
   - Query format: URL lookup adapter
   - Target threat focus: Active phishing domains & target URLs
2. **URLhaus (Abuse.ch)**
   - Query format: Host / URL lookup adapter
   - Target threat focus: Malware distribution sites & malicious payloads

## Optional Threat Intelligence Providers
1. **VirusTotal**
   - Configurable API key adapter.
   - Used when configured, but not a mandatory dependency for $0 operation.

## Provider Response Mapping
Every threat intel provider adapter returns a standardized result:
- `MATCH`: Known malicious / phishing indicator found.
- `NO_MATCH`: Indicator not present in database (*does NOT equal safe*).
- `UNAVAILABLE`: Provider offline or timed out.
- `RATE_LIMITED`: Provider query limit reached.
- `ERROR`: Exception occurred during adapter request.

## Confidence Calculation
- Provider failures degrade scan `confidence` (e.g. from HIGH to MODERATE).
- Provider failures never force a risk score override to zero or force a false "SAFE" badge.

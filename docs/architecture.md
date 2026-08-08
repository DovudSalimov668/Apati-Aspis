# APATI ASPIS — Architecture Overview

## Overview
APATI ASPIS is a modular monolith application for analyzing suspicious digital content (URLs, text messages, QR codes, images/screenshots) and providing security advice and educational checkups.

```
                    APATI ASPIS
                         │
              ┌──────────▼──────────┐
              │ React + TypeScript  │
              │ Vite + Tailwind     │
              └──────────┬──────────┘
                         │ REST / JSON
                         ▼
              ┌─────────────────────┐
              │       FastAPI       │
              │      Pydantic       │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Analysis         Providers        Database
        │                │                │
   ┌────┴────┐      ┌────┴────┐        SQLite
   │         │      │         │
Normalize   Risk   PhishTank URLhaus
SSRF       Engine
Heuristics             │
Evidence          Optional VT
   │
   └──────────────┬───────────────┐
                  ▼               ▼
             Gemini API       DNS/RDAP
```

## Layer Architecture

1. **Frontend Layer (React + Vite + TypeScript + Tailwind CSS)**
   - Responsible for presentation, accessibility, input intake, structured visualization of evidence, risk scoring, and interactive security checkups.

2. **Backend API Layer (FastAPI + Pydantic v2)**
   - Modular monolith hosting REST endpoints for `/api/scan/*`, `/api/checkup/*`, `/api/password/*`, and `/health`.

3. **Deterministic Analysis Engine**
   - **URL Normalizer & Validator:** Handles scheme, port, IDN/punycode, URL encoding, canonicalization.
   - **SSRF Defender:** Validates target IPs against private/reserved ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`, IPv6 loopback/link-local) before initiating any network connections.
   - **DNS & RDAP Extractors:** Evaluates domain registration age, DNS resolution records, and infrastructure attributes.
   - **Threat Intelligence Adapters:** Queries PhishTank, URLhaus, and optional VirusTotal with strict timeout and fallback handling.
   - **Deterministic Risk Engine:** Calculates standard risk scores (0–100) based on weighted evidence signals.

4. **AI Explanation Layer (Gemini API)**
   - Receives deterministic risk results + extracted evidence to synthesize clear, non-jargon explanations, why-risky points, and actionable guidance for non-expert users.
   - *Gemini never alters or acts as the authoritative security engine score.*

5. **Persistence Layer (SQLite + SQLAlchemy 2 + Alembic)**
   - Stores non-sensitive scan metadata, timestamps, risk classifications, and checkup summaries. Plaintext passwords or sensitive credentials are never stored or logged.

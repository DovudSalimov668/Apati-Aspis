# 🛡️ APATI ASPIS — Shield Against Digital Deception

> **Tagline:** Digital Safety Platform to Detect Deception, Understand Risk, and Take Safer Actions.

APATI ASPIS is a security-minded, free-to-demo digital safety platform designed to analyze suspicious URLs, SMS/email messages, QR codes, screenshots, password breach risks, and personal security habits.

---

## ✨ Features & Capabilities

1. **URL Scanner & Normalizer:**
   - Canonicalizes scheme, host, Punycode/IDN domains, ports, and query parameters.
   - Heuristics engine evaluating 9 structural risk signals (direct IP hosts, non-standard ports, `@` symbol userinfo, executable path extensions, scam TLDs).

2. **SSRF Protection Shield (Mandatory Defense):**
   - Pre-flight DNS resolution checking all IPv4/IPv6 addresses against prohibited ranges (`127.0.0.1`, `::1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254` cloud metadata).
   - Protects against DNS rebinding and unsafe redirect loops.

3. **Multi-Provider Threat Intelligence:**
   - Concurrent async queries to **Google Safe Browsing API**, **URLhaus API**, and optional **VirusTotal API** with 5-minute TTL caching.

4. **Deterministic Risk Engine:**
   - Authoritative security decision layer returning risk scores (`0–100`), 4 risk tiers (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`), and confidence ratings (`HIGH`, `MEDIUM`, `LOW`).

5. **Gemini AI Explanation Layer:**
   - Synthesizes clear, non-technical explanations (`summary`, `why_risky`, `recommended_actions`, `education`).
   - Includes automatic **Deterministic Fallback Engine** if Gemini API key is missing or rate-limited.
   - Built-in prompt injection protection (`<UNTRUSTED_USER_CONTENT>` encapsulation).

6. **Multi-Input Analysis:**
   - **Message / Text:** Social engineering language detection (urgency, credential requests, payment demands, brand impersonation) + URL extraction.
   - **QR Code:** Local open-source decoding via `Pillow` + `pyzbar`.
   - **Image / Screenshot:** Decodes embedded QR codes with local OCR fallback.

7. **Digital Security Checkup:**
   - 12 deterministic questions across 6 categories (phishing, password hygiene, MFA, social engineering, payment safety, device security).

8. **Password Breach Checker:**
   - Uses **Have I Been Pwned (HIBP)** with **K-Anonymity SHA-1 prefixing**. Plaintext passwords are **never** logged, stored, or sent across the network.

9. **SQLite Database Persistence:**
   - Persists scan history and checkup results locally via SQLAlchemy 2 & Alembic (`apati_aspis.db`).

10. **Hackathon Demo Mode:**
    - Simulated demo scenarios (`POST /api/scan/demo` for `safe`, `moderate`, `high`, `critical`) clearly labeled `[DEMO / SIMULATED RESULT]`.

---

## 🛠️ Technology Stack

- **Frontend:** React 18, TypeScript 5, Vite 5, Tailwind CSS 3.4, Lucide React icons.
- **Backend:** Python 3.12+, FastAPI, Pydantic v2, HTTPX async networking.
- **Database:** SQLite with SQLAlchemy 2 ORM & Alembic migrations.
- **Testing:** Pytest (81 backend tests) & Vitest (1 frontend test).

---

## 🚀 Quick Start Guide

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows PowerShell:
.venv/Scripts/Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
# In PowerShell:
$env:PATH = "C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Microsoft\VisualStudio\NodeJs;" + $env:PATH
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser!

---

## ⚙️ Environment Configuration (`.env`)

```env
APP_ENV=development
APP_PORT=8000
DEBUG=True

# Gemini AI API Key (Optional — Local fallback active if empty)
GEMINI_API_KEY=

# Threat Intelligence API Keys
GOOGLE_SAFE_BROWSING_API_KEY=
URLHAUS_AUTH_KEY=
VIRUSTOTAL_API_KEY=

# Database
DATABASE_URL=sqlite:///./apati_aspis.db
```

---

## 🧪 Running Automated Tests

```bash
# Backend Test Suite (81 tests)
backend/.venv/Scripts/python -m pytest backend/tests

# Frontend Vitest Suite
cd frontend
npx vitest run
```

---

## ⚠️ Disclaimer

> APATI ASPIS provides risk analysis and educational guidance for digital safety. It does not guarantee that an indicator is completely safe or malicious and should not replace professional enterprise security analysis.

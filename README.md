# APATI ASPIS — Shield Against Digital Deception

APATI ASPIS is a digital-safety platform designed to analyze suspicious URLs, messages, QR codes, and screenshots to detect risk, explain threat indicators, and empower users with actionable security advice.

---

## Technical Architecture

- **Frontend:** React + TypeScript + Vite + Tailwind CSS + Lucide React
- **Backend:** Python 3.12+ + FastAPI + Pydantic v2 + SQLAlchemy 2
- **Database:** SQLite
- **AI Explanation Layer:** Gemini API (Direct integration)
- **Threat Intelligence:** PhishTank, URLhaus, optional VirusTotal

---

## Project Structure

```text
apati-aspis/
├── frontend/             # React + Vite TypeScript Frontend
│   ├── src/
│   │   ├── components/   # Reusable UI Components (Header, Card, Alert, Button, Input, RiskBadge)
│   │   ├── services/     # API Client Service
│   │   └── App.tsx       # Main Application Shell
│   ├── package.json
│   └── vite.config.ts
│
├── backend/              # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py       # Server entrypoint & middleware
│   │   ├── config.py     # Pydantic environment configuration
│   │   ├── core/         # Exception handlers & core logic
│   │   ├── db/           # SQLAlchemy 2 database session
│   │   ├── api/          # REST API routers
│   │   ├── services/     # Business logic services
│   │   └── analysis/     # Deterministic risk engine & analyzers
│   ├── tests/            # Pytest test suite
│   └── requirements.txt
│
├── docs/                 # System Architecture & Specs
│   ├── architecture.md
│   ├── api.md
│   ├── security.md
│   └── threat-intelligence.md
│
├── .env.example          # Environment variables template
├── .gitignore
├── GEMINI.md             # Primary project specification
└── README.md
```

---

## Quickstart Setup & Local Execution

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** & `npm`

---

### 1. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

---

### 2. Backend Setup & Local Server

1. Navigate to `backend/` and create a virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   ```

2. Activate virtual environment:
   - **Windows:** `.venv\Scripts\activate`
   - **macOS/Linux:** `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. Verify server health check:
   Open [http://localhost:8000/health](http://localhost:8000/health)

---

### 3. Backend Test Suite

Run pytest in the `backend/` directory:
```bash
python -m pytest backend/tests
```

---

### 4. Frontend Setup & Local Execution

1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Install npm packages:
   ```bash
   npm install
   ```

3. Start Vite development server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000)

4. Run frontend tests:
   ```bash
   npm test
   ```

---

## Security Disclaimer

APATI ASPIS provides risk analysis and educational guidance. It does not guarantee that an indicator is safe or malicious and should not replace professional security analysis.

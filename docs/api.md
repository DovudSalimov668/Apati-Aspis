# APATI ASPIS — API Specification

## Baseline Endpoints

### Health Check
- `GET /health`
  - **Response:** `200 OK`
  - **Payload:**
    ```json
    {
      "status": "ok",
      "service": "APATI ASPIS API",
      "version": "0.1.0"
    }
    ```

---

## Scanner Endpoints

### 1. URL Analysis
- `POST /api/scan/url`
  - **Payload:**
    ```json
    {
      "url": "https://example.com"
    }
    ```
  - **Response:**
    ```json
    {
      "indicator": "https://example.com",
      "risk_score": 10,
      "risk_level": "LOW",
      "confidence": "HIGH",
      "evidence": {},
      "explanation": {
        "summary": "This site appears low risk.",
        "why_risky": [],
        "recommended_actions": ["Verify site certificate if entering sensitive information."]
      }
    }
    ```

### 2. Message Analysis
- `POST /api/scan/message`
  - **Payload:**
    ```json
    {
      "message": "Your account has been suspended. Click http://suspicious-link.com to reactivate."
    }
    ```

### 3. QR Code Analysis
- `POST /api/scan/qr`
  - **Payload:** `multipart/form-data` with `file`

### 4. Image / Screenshot OCR Analysis
- `POST /api/scan/image`
  - **Payload:** `multipart/form-data` with `file`

---

## Security Checkup Endpoints

### 1. Retrieve Questions
- `GET /api/checkup/questions`

### 2. Submit Checkup
- `POST /api/checkup/submit`
  - **Payload:** User responses to questionnaire items.

---

## Password Check Endpoint

### Check Password Breach Status
- `POST /api/password/check`
  - **Payload:**
    ```json
    {
      "password": "user_submitted_string"
    }
    ```
  - *Uses k-Anonymity (HIBP Pwned Passwords API). Raw passwords are never transmitted, stored, or logged.*

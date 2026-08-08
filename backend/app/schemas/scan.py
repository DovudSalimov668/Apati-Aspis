from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class UrlScanRequest(BaseModel):
    url: str = Field(..., description="Target URL to analyze for security risk", json_schema_extra={"example": "https://example.com"})

class MessageScanRequest(BaseModel):
    message: str = Field(..., description="Raw SMS, email, or chat text to analyze", json_schema_extra={"example": "URGENT: Verify your account immediately at http://login.example.com"})

class HeuristicSignalSchema(BaseModel):
    code: str
    severity: str
    message: str
    score_impact: int

class GeminiExplanationSchema(BaseModel):
    summary: str
    why_risky: List[str]
    what_to_do: List[str]
    what_not_to_do: List[str]
    education: List[str]


class UrlScanResponse(BaseModel):
    raw_url: str
    normalized_url: str
    is_valid: bool
    ssrf_blocked: bool
    ssrf_blocked_reason: Optional[str] = None
    domain: str
    resolved_ips: List[str]
    heuristics: List[HeuristicSignalSchema]
    evidence: Dict[str, Any]
    reasons: List[str]
    risk_score: int
    risk_level: str
    confidence: str
    explanation: GeminiExplanationSchema

class MessageScanResponse(BaseModel):
    raw_message: str
    extracted_urls: List[str]
    heuristics: List[HeuristicSignalSchema]
    url_scans: List[UrlScanResponse]
    evidence: Dict[str, Any]
    reasons: List[str]
    risk_score: int
    risk_level: str
    confidence: str
    explanation: GeminiExplanationSchema

class QrScanResponse(BaseModel):
    decoded_text: Optional[str]
    payload_type: str  # 'URL' or 'TEXT'
    image_format: str
    image_size_bytes: int
    scan_result: Optional[Dict[str, Any]]
    evidence: Dict[str, Any]
    reasons: List[str]
    risk_score: int
    risk_level: str
    confidence: str
    explanation: GeminiExplanationSchema

class ImageScanResponse(BaseModel):
    ocr_status: str  # 'COMPLETED', 'OCR_UNAVAILABLE', 'FAILED'
    extracted_text: Optional[str]
    qr_detected: bool
    scan_result: Optional[Dict[str, Any]]
    evidence: Dict[str, Any]
    reasons: List[str]
    risk_score: int
    risk_level: str
    confidence: str
    explanation: GeminiExplanationSchema

from fastapi import APIRouter, File, UploadFile, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.scan import (
    UrlScanRequest, UrlScanResponse,
    MessageScanRequest, MessageScanResponse,
    QrScanResponse, ImageScanResponse,
    HeuristicSignalSchema, GeminiExplanationSchema
)
from app.analysis.normalizer import normalize_url
from app.analysis.ssrf import validate_ssrf
from app.analysis.heuristics import evaluate_heuristics
from app.analysis.message_analyzer import extract_urls_from_text, evaluate_message_heuristics
from app.analysis.qr_decoder import decode_qr_image_bytes
from app.analysis.ocr import extract_text_from_image_bytes
from app.analysis.risk_engine import calculate_risk
from app.services.threat_intel.manager import threat_intel_manager
from app.services.gemini_service import explain_scan_result, generate_fallback_explanation
from app.services.history_service import save_scan_record
from app.core.errors import ValidationException

scan_router = APIRouter(prefix="/scan", tags=["Scan"])

class DemoScanRequest(BaseModel):
    scenario: str = Field(..., description="Demo scenario: 'safe', 'moderate', 'high', or 'critical'")

async def process_single_url_analysis(raw_url: str) -> Dict[str, Any]:
    norm = normalize_url(raw_url)
    if not norm.is_valid:
        assessment = calculate_risk(norm, validate_ssrf(""), [], {})
        explanation = generate_fallback_explanation(assessment.score, assessment.level, assessment.reasons)
        return UrlScanResponse(
            raw_url=raw_url,
            normalized_url=norm.normalized_url or raw_url,
            is_valid=False,
            ssrf_blocked=False,
            ssrf_blocked_reason=norm.error_message,
            domain=norm.ascii_hostname,
            resolved_ips=[],
            heuristics=[],
            evidence={"normalizer_error": norm.error_message},
            reasons=assessment.reasons,
            risk_score=assessment.score,
            risk_level=assessment.level,
            confidence=assessment.confidence,
            explanation=GeminiExplanationSchema(**explanation.model_dump())
        ).model_dump()

    ssrf = validate_ssrf(norm.ascii_hostname, norm.port or (80 if norm.scheme == "http" else 443))
    if not ssrf.is_safe:
        assessment = calculate_risk(norm, ssrf, [], {})
        explanation = generate_fallback_explanation(assessment.score, assessment.level, assessment.reasons)
        return UrlScanResponse(
            raw_url=raw_url,
            normalized_url=norm.normalized_url,
            is_valid=True,
            ssrf_blocked=True,
            ssrf_blocked_reason=ssrf.blocked_reason,
            domain=norm.ascii_hostname,
            resolved_ips=ssrf.resolved_ips,
            heuristics=[],
            evidence={
                "ssrf_check": ssrf.to_dict(),
                "normalization": norm.to_dict()
            },
            reasons=assessment.reasons,
            risk_score=assessment.score,
            risk_level=assessment.level,
            confidence=assessment.confidence,
            explanation=GeminiExplanationSchema(**explanation.model_dump())
        ).model_dump()

    heuristic_signals, _ = evaluate_heuristics(norm)
    threat_intel = await threat_intel_manager.query_all(norm.normalized_url, norm.ascii_hostname)
    assessment = calculate_risk(norm, ssrf, heuristic_signals, threat_intel)

    evidence_object = {
        "normalization": norm.to_dict(),
        "ssrf_check": ssrf.to_dict(),
        "heuristics": [sig.to_dict() for sig in heuristic_signals],
        "threat_intelligence": threat_intel
    }

    explanation = await explain_scan_result(
        indicator=norm.normalized_url,
        risk_score=assessment.score,
        risk_level=assessment.level,
        confidence=assessment.confidence,
        reasons=assessment.reasons,
        evidence=evidence_object
    )

    return UrlScanResponse(
        raw_url=raw_url,
        normalized_url=norm.normalized_url,
        is_valid=True,
        ssrf_blocked=False,
        domain=norm.ascii_hostname,
        resolved_ips=ssrf.resolved_ips,
        heuristics=[
            HeuristicSignalSchema(
                code=sig.code,
                severity=sig.severity,
                message=sig.message,
                score_impact=sig.score_impact
            ) for sig in heuristic_signals
        ],
        evidence=evidence_object,
        reasons=assessment.reasons,
        risk_score=assessment.score,
        risk_level=assessment.level,
        confidence=assessment.confidence,
        explanation=GeminiExplanationSchema(**explanation.model_dump())
    ).model_dump()


@scan_router.post("/url", response_model=UrlScanResponse)
async def scan_url(payload: UrlScanRequest, db: Session = Depends(get_db)):
    raw_input = payload.url
    if not raw_input or not raw_input.strip():
        raise ValidationException("URL input parameter cannot be empty.")
    result_dict = await process_single_url_analysis(raw_input.strip())
    
    save_scan_record(
        db=db,
        scan_type="url",
        indicator=result_dict.get("normalized_url", raw_input),
        domain=result_dict.get("domain"),
        risk_score=result_dict.get("risk_score", 0),
        risk_level=result_dict.get("risk_level", "LOW"),
        confidence=result_dict.get("confidence", "HIGH"),
        reasons=result_dict.get("reasons", []),
        evidence=result_dict.get("evidence", {})
    )

    return UrlScanResponse(**result_dict)


@scan_router.post("/message", response_model=MessageScanResponse)
async def scan_message(payload: MessageScanRequest, db: Session = Depends(get_db)):
    raw_text = payload.message
    if not raw_text or not raw_text.strip():
        raise ValidationException("Message text parameter cannot be empty.")

    text_content = raw_text.strip()
    extracted_urls = extract_urls_from_text(text_content)
    msg_signals, msg_score = evaluate_message_heuristics(text_content)

    url_scan_results = []
    max_url_score = 0
    url_evidence_list = []
    
    for url in extracted_urls:
        res = await process_single_url_analysis(url)
        url_scan_results.append(res)
        max_url_score = max(max_url_score, res.get("risk_score", 0))
        url_evidence_list.append(res.get("evidence", {}))

    combined_score = min(100, max(msg_score, max_url_score) + (10 if (msg_score > 0 and max_url_score > 0) else 0))

    if combined_score >= 75:
        risk_level = "CRITICAL"
    elif combined_score >= 50:
        risk_level = "HIGH"
    elif combined_score >= 25:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    reasons = [sig.message for sig in msg_signals]
    for res in url_scan_results:
        reasons.extend([f"Embedded Link ({res.get('normalized_url')}): {r}" for r in res.get("reasons", [])])

    if not reasons:
        reasons.append("No obvious risk signals detected in message content.")

    evidence_object = {
        "raw_message": text_content,
        "extracted_urls": extracted_urls,
        "message_heuristics": [sig.to_dict() for sig in msg_signals],
        "url_scans": url_evidence_list
    }

    explanation = await explain_scan_result(
        indicator=text_content[:150],
        risk_score=combined_score,
        risk_level=risk_level,
        confidence="HIGH",
        reasons=reasons,
        evidence=evidence_object
    )

    save_scan_record(
        db=db,
        scan_type="message",
        indicator=text_content[:200],
        domain=extracted_urls[0] if extracted_urls else None,
        risk_score=combined_score,
        risk_level=risk_level,
        confidence="HIGH",
        reasons=reasons,
        evidence=evidence_object
    )

    return MessageScanResponse(
        raw_message=text_content,
        extracted_urls=extracted_urls,
        heuristics=[
            HeuristicSignalSchema(
                code=sig.code,
                severity=sig.severity,
                message=sig.message,
                score_impact=sig.score_impact
            ) for sig in msg_signals
        ],
        url_scans=[UrlScanResponse(**res) for res in url_scan_results],
        evidence=evidence_object,
        reasons=reasons,
        risk_score=combined_score,
        risk_level=risk_level,
        confidence="HIGH",
        explanation=GeminiExplanationSchema(**explanation.model_dump())
    )


@scan_router.post("/qr", response_model=QrScanResponse)
async def scan_qr(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file or not file.filename:
        raise ValidationException("QR image file must be uploaded.")

    image_bytes = await file.read()
    qr_res = decode_qr_image_bytes(image_bytes)

    if not qr_res.success:
        explanation = generate_fallback_explanation(100, "CRITICAL", [qr_res.error_message or "QR decoding failed"])
        res_payload = QrScanResponse(
            decoded_text=None,
            payload_type="UNKNOWN",
            image_format=qr_res.image_format,
            image_size_bytes=qr_res.image_size_bytes,
            scan_result=None,
            evidence={"qr_decode": qr_res.to_dict()},
            reasons=[f"QR Code Scan Error: {qr_res.error_message}"],
            risk_score=100,
            risk_level="CRITICAL",
            confidence="HIGH",
            explanation=GeminiExplanationSchema(**explanation.model_dump())
        )
        save_scan_record(
            db=db,
            scan_type="qr",
            indicator=file.filename,
            domain=None,
            risk_score=100,
            risk_level="CRITICAL",
            confidence="HIGH",
            reasons=res_payload.reasons,
            evidence=res_payload.evidence
        )
        return res_payload

    decoded_content = qr_res.decoded_text or ""
    
    if qr_res.payload_type == "URL":
        scan_data = await process_single_url_analysis(decoded_content)
        risk_score = scan_data.get("risk_score", 0)
        risk_level = scan_data.get("risk_level", "LOW")
        reasons = scan_data.get("reasons", [])
        explanation_dict = scan_data.get("explanation", {})
        explanation = GeminiExplanationSchema(**explanation_dict)
    else:
        msg_payload = MessageScanRequest(message=decoded_content)
        msg_res = await scan_message(msg_payload, db=db)
        scan_data = msg_res.model_dump()
        risk_score = msg_res.risk_score
        risk_level = msg_res.risk_level
        reasons = msg_res.reasons
        explanation = msg_res.explanation

    res_payload = QrScanResponse(
        decoded_text=decoded_content,
        payload_type=qr_res.payload_type,
        image_format=qr_res.image_format,
        image_size_bytes=qr_res.image_size_bytes,
        scan_result=scan_data,
        evidence={"qr_decode": qr_res.to_dict(), "inner_scan": scan_data},
        reasons=reasons,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence="HIGH",
        explanation=explanation
    )

    save_scan_record(
        db=db,
        scan_type="qr",
        indicator=decoded_content,
        domain=scan_data.get("domain"),
        risk_score=risk_score,
        risk_level=risk_level,
        confidence="HIGH",
        reasons=reasons,
        evidence=res_payload.evidence
    )

    return res_payload


@scan_router.post("/image", response_model=ImageScanResponse)
async def scan_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file or not file.filename:
        raise ValidationException("Image file must be uploaded.")

    image_bytes = await file.read()
    qr_res = decode_qr_image_bytes(image_bytes)
    
    if qr_res.success:
        qr_scan_res = await scan_qr(file, db=db)
        return ImageScanResponse(
            ocr_status="COMPLETED",
            extracted_text=qr_res.decoded_text,
            qr_detected=True,
            scan_result=qr_scan_res.model_dump(),
            evidence={"qr_detected": True, "qr_payload": qr_res.to_dict()},
            reasons=qr_scan_res.reasons,
            risk_score=qr_scan_res.risk_score,
            risk_level=qr_scan_res.risk_level,
            confidence=qr_scan_res.confidence,
            explanation=qr_scan_res.explanation
        )

    ocr_res = extract_text_from_image_bytes(image_bytes)
    
    if ocr_res.available and ocr_res.extracted_text:
        msg_res = await scan_message(MessageScanRequest(message=ocr_res.extracted_text), db=db)
        return ImageScanResponse(
            ocr_status="COMPLETED",
            extracted_text=ocr_res.extracted_text,
            qr_detected=False,
            scan_result=msg_res.model_dump(),
            evidence={"ocr": ocr_res.to_dict(), "inner_scan": msg_res.model_dump()},
            reasons=msg_res.reasons,
            risk_score=msg_res.risk_score,
            risk_level=msg_res.risk_level,
            confidence=msg_res.confidence,
            explanation=msg_res.explanation
        )
    else:
        explanation = generate_fallback_explanation(0, "LOW", ["Image uploaded. OCR is uninstalled locally."])
        res_payload = ImageScanResponse(
            ocr_status=ocr_res.status,
            extracted_text=None,
            qr_detected=False,
            scan_result=None,
            evidence={"ocr": ocr_res.to_dict()},
            reasons=[f"OCR Status: {ocr_res.status}. {ocr_res.error_message or ''}"],
            risk_score=0,
            risk_level="LOW",
            confidence="MEDIUM",
            explanation=GeminiExplanationSchema(**explanation.model_dump())
        )
        save_scan_record(
            db=db,
            scan_type="image",
            indicator=file.filename,
            domain=None,
            risk_score=0,
            risk_level="LOW",
            confidence="MEDIUM",
            reasons=res_payload.reasons,
            evidence=res_payload.evidence
        )
        return res_payload


@scan_router.post("/demo", response_model=UrlScanResponse)
async def scan_demo(payload: DemoScanRequest, db: Session = Depends(get_db)):
    """
    Generates clearly labeled demo scenarios for hackathon presentations.
    Guarantees reliable demonstration even if external APIs are unreachable.
    """
    scen = payload.scenario.lower().strip()
    
    if scen == "safe":
        url = "https://example.com"
        score, level = 0, "LOW"
        reasons = ["[DEMO / SIMULATED RESULT] Valid domain name, active HTTPS encryption, zero threat reports."]
        why_risky = ["No security risks detected for this target domain."]
        actions = ["Verify site identity when submitting personal details."]
    elif scen == "moderate":
        url = "http://unusual-domain.top:8080/portal"
        score, level = 35, "MODERATE"
        reasons = ["[DEMO / SIMULATED RESULT] Non-standard web port 8080 used.", "[DEMO / SIMULATED RESULT] Top-level domain (.top) frequently associated with spam."]
        why_risky = ["Uses non-standard web port 8080.", "Uses low-cost top-level domain (.top)."]
        actions = ["Check address bar domain spelling carefully.", "Do not enter passwords unless identity is verified."]
    elif scen == "high":
        url = "http://google.com@login-secure-banking.com/verify.exe"
        score, level = 65, "HIGH"
        reasons = ["[DEMO / SIMULATED RESULT] @ symbol obfuscation in URL userinfo.", "[DEMO / SIMULATED RESULT] Path targets executable file (.exe)."]
        why_risky = ["URL uses @ symbol obfuscation to hide true destination domain.", "Target path drops an executable installer (.exe)."]
        actions = ["Do not download or launch files from this website.", "Do not enter account credentials."]
    else: # critical
        url = "http://93.184.216.34/phishing/paypal-login"
        score, level = 95, "CRITICAL"
        reasons = [
            "[DEMO / SIMULATED RESULT] THREAT MATCH: Active phishing indicator flagged in threat database.",
            "[DEMO / SIMULATED RESULT] URL targets direct IP address instead of domain name.",
            "[DEMO / SIMULATED RESULT] High confidence brand impersonation attempt."
        ]
        why_risky = ["Active threat intelligence match flagged for phishing.", "Direct IP host address bypasses standard domain name registration."]
        actions = ["Close the browser window immediately.", "Do not enter any personal credentials or financial details."]

    res = UrlScanResponse(
        raw_url=url,
        normalized_url=url,
        is_valid=True,
        ssrf_blocked=False,
        domain="demo.target.example",
        resolved_ips=["93.184.216.34"],
        heuristics=[],
        evidence={"demo_mode": True, "scenario": scen},
        reasons=reasons,
        risk_score=score,
        risk_level=level,
        confidence="HIGH",
        explanation=GeminiExplanationSchema(
            summary=f"[DEMO / SIMULATED RESULT] {level} risk scenario simulation.",
            why_risky=why_risky,
            what_to_do=actions,
            what_not_to_do=["DO NOT submit passwords or financial information on unverified demo sites."],
            education=["Always inspect the full domain name in your browser address bar before logging in."]
        )
    )


    save_scan_record(
        db=db,
        scan_type="demo",
        indicator=f"[DEMO: {scen.upper()}] {url}",
        domain="demo.target.example",
        risk_score=score,
        risk_level=level,
        confidence="HIGH",
        reasons=reasons,
        evidence=res.evidence
    )

    return res


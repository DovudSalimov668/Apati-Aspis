import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import ScanRecord, CheckupRecord

def save_scan_record(
    db: Session,
    scan_type: str,
    indicator: str,
    domain: Optional[str],
    risk_score: int,
    risk_level: str,
    confidence: str,
    reasons: List[str],
    evidence: Dict[str, Any]
) -> ScanRecord:
    """Saves a scan result record to SQLite database safely."""
    try:
        record = ScanRecord(
            scan_type=scan_type,
            indicator=indicator[:500] if indicator else "",
            domain=domain[:255] if domain else None,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            reasons_json=json.dumps(reasons) if reasons else "[]",
            evidence_json=json.dumps(evidence) if evidence else "{}"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as exc:
        db.rollback()
        # Ensure database failures do not crash the scan API response
        return None

def get_scan_history(db: Session, limit: int = 20) -> List[ScanRecord]:
    """Retrieves recent scan records ordered by created_at desc."""
    try:
        return db.query(ScanRecord).order_by(ScanRecord.created_at.desc()).limit(limit).all()
    except Exception:
        return []

def save_checkup_record(
    db: Session,
    overall_score: int,
    security_level: str,
    weakest_category: str,
    recommendations: List[str]
) -> CheckupRecord:
    """Saves a security checkup report to SQLite database safely."""
    try:
        record = CheckupRecord(
            overall_score=overall_score,
            security_level=security_level,
            weakest_category=weakest_category[:100] if weakest_category else "None",
            recommendations_json=json.dumps(recommendations) if recommendations else "[]"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as exc:
        db.rollback()
        return None

def get_checkup_history(db: Session, limit: int = 20) -> List[CheckupRecord]:
    """Retrieves recent checkup records ordered by created_at desc."""
    try:
        return db.query(CheckupRecord).order_by(CheckupRecord.created_at.desc()).limit(limit).all()
    except Exception:
        return []

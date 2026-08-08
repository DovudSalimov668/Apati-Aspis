import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.session import Base

class ScanRecord(Base):
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_type = Column(String(20), nullable=False, index=True)  # 'url', 'message', 'qr', 'image'
    indicator = Column(String(500), nullable=False)
    domain = Column(String(255), nullable=True, index=True)
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence = Column(String(20), nullable=False)
    reasons_json = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        try:
            reasons = json.loads(self.reasons_json)
        except Exception:
            reasons = []
        try:
            evidence = json.loads(self.evidence_json)
        except Exception:
            evidence = {}

        return {
            "id": self.id,
            "scan_type": self.scan_type,
            "indicator": self.indicator,
            "domain": self.domain,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "reasons": reasons,
            "evidence": evidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CheckupRecord(Base):
    __tablename__ = "checkup_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    overall_score = Column(Integer, nullable=False)
    security_level = Column(String(20), nullable=False)
    weakest_category = Column(String(100), nullable=False)
    recommendations_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        try:
            reasons = json.loads(self.recommendations_json)
        except Exception:
            reasons = []

        return {
            "id": self.id,
            "overall_score": self.overall_score,
            "security_level": self.security_level,
            "weakest_category": self.weakest_category,
            "recommendations": reasons,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

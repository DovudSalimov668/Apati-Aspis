from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.history_service import get_scan_history, get_checkup_history

history_router = APIRouter(prefix="/history", tags=["History"])

@history_router.get("/scans")
def fetch_scan_history(limit: int = 20, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves recent scan history records from SQLite database."""
    records = get_scan_history(db, limit=limit)
    return [r.to_dict() for r in records]

@history_router.get("/checkups")
def fetch_checkup_history(limit: int = 20, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves recent security checkup records from SQLite database."""
    records = get_checkup_history(db, limit=limit)
    return [r.to_dict() for r in records]

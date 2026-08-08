from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.checkup_service import QUESTIONS, evaluate_checkup_submission, CheckupSubmissionRequest
from app.services.history_service import save_checkup_record
from app.core.errors import ValidationException

checkup_router = APIRouter(prefix="/checkup", tags=["Security Checkup"])

@checkup_router.get("/questions")
def get_checkup_questions() -> List[Dict[str, Any]]:
    """Returns the list of 12 security checkup questions (hiding points for server-side evaluation)."""
    public_questions = []
    for q in QUESTIONS:
        public_questions.append({
            "id": q.id,
            "category": q.category,
            "category_title": q.category_title,
            "question": q.question,
            "options": [
                {"id": opt.id, "text": opt.text} for opt in q.options
            ]
        })
    return public_questions

@checkup_router.post("/submit")
def submit_checkup(payload: CheckupSubmissionRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Evaluates checkup submission deterministically and saves report to database."""
    if not payload.answers or not isinstance(payload.answers, dict):
        raise ValidationException("Submission answers payload must be a non-empty object.")

    result = evaluate_checkup_submission(payload.answers)
    
    # Save checkup record to SQLite database
    save_checkup_record(
        db=db,
        overall_score=result.get("overall_score", 0),
        security_level=result.get("security_level", "LOW"),
        weakest_category=result.get("weakest_category", "None"),
        recommendations=result.get("recommendations", [])
    )

    return result

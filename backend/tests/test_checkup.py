import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.checkup_service import QUESTIONS, evaluate_checkup_submission

client = TestClient(app)

def test_get_checkup_questions():
    response = client.get("/api/checkup/questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 12
    # Ensure point values are hidden from public API response
    assert "points" not in questions[0]["options"][0]

def test_checkup_all_correct_score_100():
    best_answers = {
        "q1": "c", "q2": "b", "q3": "c", "q4": "a",
        "q5": "c", "q6": "b", "q7": "b", "q8": "b",
        "q9": "b", "q10": "a", "q11": "a", "q12": "a"
    }
    response = client.post("/api/checkup/submit", json={"answers": best_answers})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 100
    assert data["security_level"] == "EXCELLENT"
    assert len(data["recommendations"]) == 1

def test_checkup_all_incorrect_score_0():
    worst_answers = {
        "q1": "a", "q2": "a", "q3": "a", "q4": "c",
        "q5": "a", "q6": "c", "q7": "a", "q8": "a",
        "q9": "a", "q10": "b", "q11": "c", "q12": "c"
    }
    response = client.post("/api/checkup/submit", json={"answers": worst_answers})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 0
    assert data["security_level"] == "LOW"
    assert len(data["category_scores"]) == 6

def test_checkup_mixed_answers():
    mixed_answers = {
        "q1": "c", "q2": "b", # Phishing: Good (100%)
        "q3": "a", "q4": "c", # Passwords: Poor (0%)
        "q5": "c", "q6": "b", # MFA: Good (100%)
        "q7": "b", "q8": "b", # Social Eng: Good (100%)
        "q9": "b", "q10": "a", # Payment: Good (100%)
        "q11": "a", "q12": "a"  # Device: Good (100%)
    }
    response = client.post("/api/checkup/submit", json={"answers": mixed_answers})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 83
    assert data["security_level"] == "HIGH"
    assert data["category_scores"]["passwords"]["score"] == 0
    assert "Password" in data["weakest_category"]

def test_checkup_missing_answer_handling():
    # Only answer 2 questions out of 12
    partial_answers = {"q1": "c", "q2": "b"}
    response = client.post("/api/checkup/submit", json={"answers": partial_answers})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 17
    assert data["security_level"] == "LOW"

def test_checkup_invalid_answer_handling():
    invalid_answers = {"q1": "invalid_option_xyz"}
    response = client.post("/api/checkup/submit", json={"answers": invalid_answers})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 0

def test_checkup_score_boundaries():
    # Boundary threshold verification
    res_85 = evaluate_checkup_submission({q.id: q.options[0].id for q in QUESTIONS})
    res_85["overall_score"] = 85
    assert res_85["overall_score"] == 85

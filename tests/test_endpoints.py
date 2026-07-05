import sys
import os
from fastapi.testclient import TestClient

# Add the backend application directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../apps/backend')))

from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "studymateai-backend"}

def test_ready_endpoint():
    response = client.get("/ready")
    assert response.status_code == 200
    assert "ready" in response.json()["status"]

def test_chat_invalid_subject():
    # Free tier only allows physics and chemistry
    response = client.post(
        "/api/v1/chat",
        json={
            "year": "2nd PUC",
            "board": "Karnataka State Board",
            "subject": "biology",  # biology is designed but not implemented in MVP free tier
            "query": "Explain cell theory"
        }
    )
    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]

def test_chat_physics_success():
    response = client.post(
        "/api/v1/chat",
        json={
            "year": "2nd PUC",
            "board": "Karnataka State Board",
            "subject": "physics",
            "query": "Explain Ray Optics for NEET"
        }
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["answer"] is not None

def test_quiz_generation():
    response = client.post(
        "/api/v1/quiz",
        json={
            "year": "2nd PUC",
            "board": "Karnataka State Board",
            "subject": "chemistry",
            "query": "Generate quiz on Atomic Structure"
        }
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["subject"] == "chemistry"
    assert len(res_data["questions"]) > 0

def test_evaluator():
    # Make a mock evaluate request with incorrect answer to assert missing points output
    response = client.post(
        "/api/v1/evaluate",
        json={
            "questions": [
                {"id": 1, "correct_option": "A", "explanation": "Option A is correct"}
            ],
            "student_answers": {
                "1": "B"
            },
            "subject": "physics"
        }
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["score"] == 0
    assert res_data["max_score"] == 1
    assert len(res_data["missing_points"]) > 0


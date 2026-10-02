import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_calculate_nutrition_api(client):
    payload = {
        "weight_kg": 75.0,
        "height_cm": 178.0,
        "age": 28,
        "sex": "male",
        "activity_level": "moderate",
        "goal": "weight_loss"
    }
    response = client.post("/api/nutrition/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["bmr"] > 1000
    assert data["tdee"] > data["bmr"]
    assert data["target_calories"] < data["tdee"]
    assert data["target_protein_g"] > 100


def test_foods_api(client):
    response = client.get("/api/foods?query=roti")
    assert response.status_code == 200
    foods = response.json()
    assert len(foods) > 0
    assert any("roti" in f["name"].lower() for f in foods)


def test_rag_query_api(client):
    payload = {"query": "What is protein?"}
    response = client.post("/api/rag/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "protein" in data["answer"].lower()
    assert len(data["retrieved_chunks"]) > 0
    assert data["confidence"] > 0


def test_chat_api(client):
    payload = {"message": "What should I eat for breakfast?"}
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert len(data["content"]) > 10

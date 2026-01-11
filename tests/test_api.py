from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_chat_validation_failure():
    # Helper to check validation without needing DB
    response = client.post("/chat", json={})
    assert response.status_code == 422

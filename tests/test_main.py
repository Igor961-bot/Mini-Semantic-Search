import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Sprawdza czy główna strona / interfejs odpowiada pomyślnie"""
    response = client.get("/")
    assert response.status_code == 200

def test_swagger_docs():
    """Sprawdza czy dokumentacja API (Swagger) ładuje się poprawnie"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_invalid_endpoint():
    """Sprawdza czy system poprawnie zwraca 404 dla nieistniejących ścieżek"""
    response = client.get("/jakis-dziwny-endpoint-ktorego-nie-ma")
    assert response.status_code == 404
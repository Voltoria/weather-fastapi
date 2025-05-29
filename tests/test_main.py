from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Прогноз погоды" in response.text

def test_post_valid_city(monkeypatch):
    # Подменим http-запрос, чтобы не дергать настоящий API
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "list": [
                    {
                        "dt_txt": "2025-05-28 12:00:00",
                        "main": {"temp": 20.5},
                        "weather": [{"description": "ясно"}],
                        "wind": {"speed": 3.5}
                    }
                ]
            }

    async def mock_get(*args, **kwargs):
        return MockResponse()

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.post("/", data={"city": "Moscow"})
    assert response.status_code == 200
    assert "Прогноз на 5 дней для Moscow" in response.text
    assert "Температура: 20.5 °C" in response.text

def test_post_invalid_city(monkeypatch):
    class MockResponse:
        status_code = 404
        def json(self):
            return {"message": "город не найден"}

    async def mock_get(*args, **kwargs):
        return MockResponse()

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.post("/", data={"city": "FakeCity123"})
    assert response.status_code == 200
    assert "Ошибка: город не найден" in response.text

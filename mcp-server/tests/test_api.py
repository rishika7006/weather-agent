import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


MOCK_CURRENT = {
    "city": "Tokyo", "country": "JP",
    "temperature_f": 72.5, "feels_like_f": 70.1,
    "humidity": 55, "description": "clear sky", "icon": "01d",
    "wind_speed_mph": 8.2, "pressure_hpa": 1013, "visibility_m": 10000,
}

MOCK_FORECAST = {
    "city": "Tokyo", "country": "JP",
    "forecast": [
        {"date": "2026-03-05", "temp_high_f": 72.0, "temp_low_f": 68.0,
         "avg_humidity": 47.5, "conditions": "sunny"},
    ],
}

MOCK_AIR = {
    "city": "Tokyo", "country": "JP",
    "aqi": 2, "aqi_label": "Fair",
    "pm2_5": 12.5, "pm10": 20.0, "co": 230.0, "no2": 15.0, "o3": 68.0,
}


@pytest.fixture
def mock_weather_service():
    service = MagicMock()
    service.get_current_weather = AsyncMock(return_value=(MOCK_CURRENT, False))
    service.get_forecast = AsyncMock(return_value=(MOCK_FORECAST, False))
    service.get_air_quality = AsyncMock(return_value=(MOCK_AIR, False))
    service.cache = MagicMock()
    service.cache.stats.return_value = {
        "size": 5, "capacity": 128, "hits": 10, "misses": 3, "hit_rate": 0.769,
    }
    return service


@pytest.fixture
def client(mock_weather_service):
    with patch("main.weather_service", mock_weather_service):
        from main import app
        yield TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp-server"


class TestCacheStatsEndpoint:
    def test_cache_stats(self, client):
        resp = client.get("/api/cache/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["hits"] == 10


class TestCurrentWeatherEndpoint:
    def test_success(self, client, mock_weather_service):
        resp = client.get("/api/weather/current", params={"city": "Tokyo"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["city"] == "Tokyo"
        assert data["data"]["temperature_f"] == 72.5
        assert data["cached"] is False
        mock_weather_service.get_current_weather.assert_called_once_with("Tokyo")

    def test_cached_response(self, client, mock_weather_service):
        mock_weather_service.get_current_weather = AsyncMock(
            return_value=(MOCK_CURRENT, True)
        )
        resp = client.get("/api/weather/current", params={"city": "Tokyo"})
        assert resp.status_code == 200
        assert resp.json()["cached"] is True

    def test_missing_city_param(self, client):
        resp = client.get("/api/weather/current")
        assert resp.status_code == 422

    def test_city_not_found(self, client, mock_weather_service):
        mock_weather_service.get_current_weather = AsyncMock(
            side_effect=ValueError("City 'Xyz' not found.")
        )
        resp = client.get("/api/weather/current", params={"city": "Xyz"})
        assert resp.status_code == 404

    def test_api_error(self, client, mock_weather_service):
        mock_weather_service.get_current_weather = AsyncMock(
            side_effect=RuntimeError("timeout")
        )
        resp = client.get("/api/weather/current", params={"city": "Tokyo"})
        assert resp.status_code == 500


class TestForecastEndpoint:
    def test_success(self, client, mock_weather_service):
        resp = client.get("/api/weather/forecast", params={"city": "Tokyo", "days": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["cached"] is False
        assert len(data["data"]["forecast"]) == 1
        mock_weather_service.get_forecast.assert_called_once_with("Tokyo", 3)

    def test_default_days(self, client, mock_weather_service):
        resp = client.get("/api/weather/forecast", params={"city": "Tokyo"})
        assert resp.status_code == 200
        mock_weather_service.get_forecast.assert_called_once_with("Tokyo", 3)

    def test_invalid_days(self, client):
        resp = client.get("/api/weather/forecast", params={"city": "Tokyo", "days": 10})
        assert resp.status_code == 422


class TestAirQualityEndpoint:
    def test_success(self, client, mock_weather_service):
        resp = client.get("/api/weather/air-quality", params={"city": "Tokyo"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["aqi"] == 2
        assert data["data"]["aqi_label"] == "Fair"
        assert data["cached"] is False
        mock_weather_service.get_air_quality.assert_called_once_with("Tokyo")

import pytest
import httpx
from unittest.mock import patch, MagicMock
from direct_weather import DirectWeatherClient


GEOCODE_RESPONSE = [
    {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo", "country": "JP"}
]

CURRENT_WEATHER_RESPONSE = {
    "main": {"temp": 72.5, "feels_like": 70.1, "humidity": 55, "pressure": 1013},
    "weather": [{"description": "clear sky", "icon": "01d"}],
    "wind": {"speed": 8.2},
    "visibility": 10000,
}

FORECAST_RESPONSE = {
    "list": [
        {
            "dt_txt": "2026-03-05 12:00:00",
            "main": {"temp": 68.0, "humidity": 50},
            "weather": [{"description": "sunny"}],
        },
        {
            "dt_txt": "2026-03-05 15:00:00",
            "main": {"temp": 72.0, "humidity": 45},
            "weather": [{"description": "sunny"}],
        },
    ]
}

AIR_QUALITY_RESPONSE = {
    "list": [{
        "main": {"aqi": 2},
        "components": {"pm2_5": 12.5, "pm10": 20.0, "co": 230.0, "no2": 15.0, "o3": 68.0},
    }]
}


def _mock_response(json_data):
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


@pytest.fixture
def client():
    return DirectWeatherClient()


class TestDirectWeatherClient:
    @patch("direct_weather.httpx.get")
    def test_geocode(self, mock_get, client):
        mock_get.return_value = _mock_response(GEOCODE_RESPONSE)
        result = client._geocode("Tokyo")
        assert result["lat"] == 35.6762
        assert result["name"] == "Tokyo"

    @patch("direct_weather.httpx.get")
    def test_geocode_not_found(self, mock_get, client):
        mock_get.return_value = _mock_response([])
        with pytest.raises(ValueError, match="not found"):
            client._geocode("Fakecity")

    @patch("direct_weather.httpx.get")
    def test_get_current_weather(self, mock_get, client):
        mock_get.side_effect = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(CURRENT_WEATHER_RESPONSE),
        ]
        result = client.get_current_weather("Tokyo")
        assert result["city"] == "Tokyo"
        assert result["temperature_f"] == 72.5
        assert result["humidity"] == 55

    @patch("direct_weather.httpx.get")
    def test_get_forecast(self, mock_get, client):
        mock_get.side_effect = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(FORECAST_RESPONSE),
        ]
        result = client.get_forecast("Tokyo", days=1)
        assert result["city"] == "Tokyo"
        assert len(result["forecast"]) == 1
        assert result["forecast"][0]["temp_high_f"] == 72.0

    @patch("direct_weather.httpx.get")
    def test_get_air_quality(self, mock_get, client):
        mock_get.side_effect = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(AIR_QUALITY_RESPONSE),
        ]
        result = client.get_air_quality("Tokyo")
        assert result["aqi"] == 2
        assert result["aqi_label"] == "Fair"
        assert result["pm2_5"] == 12.5

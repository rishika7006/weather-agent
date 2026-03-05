import pytest
import httpx
from unittest.mock import patch, MagicMock


MOCK_CURRENT_RESPONSE = {
    "data": {
        "city": "Tokyo", "country": "JP",
        "temperature_f": 72.5, "feels_like_f": 70.1,
        "humidity": 55, "description": "clear sky",
        "wind_speed_mph": 8.2, "pressure_hpa": 1013,
        "visibility_m": 10000,
    },
    "cached": False,
}

MOCK_CURRENT_CACHED_RESPONSE = {
    **MOCK_CURRENT_RESPONSE,
    "cached": True,
}

MOCK_FORECAST_RESPONSE = {
    "data": {
        "city": "Tokyo", "country": "JP",
        "forecast": [
            {"date": "2026-03-05", "temp_high_f": 72.0, "temp_low_f": 68.0,
             "conditions": "sunny", "avg_humidity": 47.5},
            {"date": "2026-03-06", "temp_high_f": 65.0, "temp_low_f": 60.0,
             "conditions": "cloudy", "avg_humidity": 60.0},
        ],
    },
    "cached": False,
}

MOCK_AIR_RESPONSE = {
    "data": {
        "city": "Tokyo", "country": "JP",
        "aqi": 2, "aqi_label": "Fair",
        "pm2_5": 12.5, "pm10": 20.0, "co": 230.0, "no2": 15.0, "o3": 68.0,
    },
    "cached": False,
}

MOCK_DIRECT_CURRENT = {
    "city": "Tokyo", "country": "JP",
    "temperature_f": 72.5, "feels_like_f": 70.1,
    "humidity": 55, "description": "clear sky",
    "wind_speed_mph": 8.2, "pressure_hpa": 1013,
    "visibility_m": 10000,
}

MOCK_DIRECT_FORECAST = {
    "city": "Tokyo", "country": "JP",
    "forecast": [
        {"date": "2026-03-05", "temp_high_f": 72.0, "temp_low_f": 68.0,
         "conditions": "sunny", "avg_humidity": 47.5},
    ],
}

MOCK_DIRECT_AIR = {
    "city": "Tokyo", "country": "JP",
    "aqi": 2, "aqi_label": "Fair",
    "pm2_5": 12.5, "pm10": 20.0, "co": 230.0, "no2": 15.0, "o3": 68.0,
}


def _mock_httpx_response(json_data, status_code=200):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=resp
        )
    return resp


class TestGetCurrentWeatherTool:
    @patch("tools.httpx.get")
    def test_success_via_mcp(self, mock_get):
        mock_get.return_value = _mock_httpx_response(MOCK_CURRENT_RESPONSE)
        from tools import get_current_weather
        result = get_current_weather.invoke({"city": "Tokyo"})
        assert "Tokyo" in result
        assert "72.5\u00b0F" in result
        assert "[CACHED]" not in result
        assert "[FALLBACK]" not in result

    @patch("tools.httpx.get")
    def test_cached_response_has_marker(self, mock_get):
        mock_get.return_value = _mock_httpx_response(MOCK_CURRENT_CACHED_RESPONSE)
        from tools import get_current_weather
        result = get_current_weather.invoke({"city": "Tokyo"})
        assert "[CACHED]" in result

    @patch("tools.httpx.get")
    def test_http_error_404_no_fallback(self, mock_get):
        error_resp = _mock_httpx_response({"detail": "City not found"}, status_code=404)
        mock_get.return_value = error_resp
        from tools import get_current_weather
        result = get_current_weather.invoke({"city": "Fakecity"})
        assert "Error fetching weather" in result
        assert "[FALLBACK]" not in result

    @patch("tools.get_direct_client")
    @patch("tools.httpx.get")
    def test_mcp_down_triggers_fallback(self, mock_get, mock_direct_client):
        mock_get.side_effect = httpx.ConnectError("refused")
        mock_client = MagicMock()
        mock_client.get_current_weather.return_value = MOCK_DIRECT_CURRENT
        mock_direct_client.return_value = mock_client

        from tools import get_current_weather
        result = get_current_weather.invoke({"city": "Tokyo"})
        assert "Tokyo" in result
        assert "72.5\u00b0F" in result
        assert "[FALLBACK]" in result
        mock_client.get_current_weather.assert_called_once_with("Tokyo")

    @patch("tools.get_direct_client")
    @patch("tools.httpx.get")
    def test_mcp_500_triggers_fallback(self, mock_get, mock_direct_client):
        mock_get.return_value = _mock_httpx_response({"detail": "Internal"}, status_code=500)
        mock_client = MagicMock()
        mock_client.get_current_weather.return_value = MOCK_DIRECT_CURRENT
        mock_direct_client.return_value = mock_client

        from tools import get_current_weather
        result = get_current_weather.invoke({"city": "Tokyo"})
        assert "[FALLBACK]" in result


class TestGetWeatherForecastTool:
    @patch("tools.httpx.get")
    def test_success_via_mcp(self, mock_get):
        mock_get.return_value = _mock_httpx_response(MOCK_FORECAST_RESPONSE)
        from tools import get_weather_forecast
        result = get_weather_forecast.invoke({"city": "Tokyo", "days": 2})
        assert "Tokyo" in result
        assert "[FALLBACK]" not in result

    @patch("tools.get_direct_client")
    @patch("tools.httpx.get")
    def test_mcp_down_triggers_fallback(self, mock_get, mock_direct_client):
        mock_get.side_effect = httpx.ConnectError("refused")
        mock_client = MagicMock()
        mock_client.get_forecast.return_value = MOCK_DIRECT_FORECAST
        mock_direct_client.return_value = mock_client

        from tools import get_weather_forecast
        result = get_weather_forecast.invoke({"city": "Tokyo", "days": 2})
        assert "Tokyo" in result
        assert "[FALLBACK]" in result


class TestGetAirQualityTool:
    @patch("tools.httpx.get")
    def test_success_via_mcp(self, mock_get):
        mock_get.return_value = _mock_httpx_response(MOCK_AIR_RESPONSE)
        from tools import get_air_quality
        result = get_air_quality.invoke({"city": "Tokyo"})
        assert "Tokyo" in result
        assert "Fair" in result
        assert "[FALLBACK]" not in result

    @patch("tools.get_direct_client")
    @patch("tools.httpx.get")
    def test_mcp_down_triggers_fallback(self, mock_get, mock_direct_client):
        mock_get.side_effect = httpx.ConnectError("refused")
        mock_client = MagicMock()
        mock_client.get_air_quality.return_value = MOCK_DIRECT_AIR
        mock_direct_client.return_value = mock_client

        from tools import get_air_quality
        result = get_air_quality.invoke({"city": "Tokyo"})
        assert "[FALLBACK]" in result

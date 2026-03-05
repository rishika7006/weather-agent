import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from services.providers.openweathermap import OpenWeatherMapProvider


@pytest.fixture
def provider():
    return OpenWeatherMapProvider(api_key="test-key", base_url="https://api.test.com")


# --- Sample API responses ---

GEOCODE_RESPONSE = [
    {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo", "country": "JP"}
]

CURRENT_WEATHER_RESPONSE = {
    "main": {
        "temp": 72.5,
        "feels_like": 70.1,
        "humidity": 55,
        "pressure": 1013,
    },
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
        {
            "dt_txt": "2026-03-06 12:00:00",
            "main": {"temp": 65.0, "humidity": 60},
            "weather": [{"description": "cloudy"}],
        },
    ]
}

AIR_QUALITY_RESPONSE = {
    "list": [
        {
            "main": {"aqi": 2},
            "components": {
                "pm2_5": 12.5,
                "pm10": 20.0,
                "co": 230.0,
                "no2": 15.0,
                "o3": 68.0,
            },
        }
    ]
}


def _mock_response(json_data, status_code=200):
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


class TestGeocode:
    @pytest.mark.asyncio
    async def test_geocode_success(self, provider):
        provider.client.get = AsyncMock(return_value=_mock_response(GEOCODE_RESPONSE))
        result = await provider.geocode("Tokyo")
        assert result["lat"] == 35.6762
        assert result["lon"] == 139.6503
        assert result["name"] == "Tokyo"
        assert result["country"] == "JP"

    @pytest.mark.asyncio
    async def test_geocode_city_not_found(self, provider):
        provider.client.get = AsyncMock(return_value=_mock_response([]))
        with pytest.raises(ValueError, match="not found"):
            await provider.geocode("Fakecity")


class TestGetCurrentWeather:
    @pytest.mark.asyncio
    async def test_current_weather_success(self, provider):
        responses = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(CURRENT_WEATHER_RESPONSE),
        ]
        provider.client.get = AsyncMock(side_effect=responses)

        result = await provider.get_current_weather("Tokyo")
        assert result["city"] == "Tokyo"
        assert result["country"] == "JP"
        assert result["temperature_f"] == 72.5
        assert result["humidity"] == 55
        assert result["description"] == "clear sky"
        assert result["wind_speed_mph"] == 8.2

    @pytest.mark.asyncio
    async def test_current_weather_propagates_geocode_error(self, provider):
        provider.client.get = AsyncMock(return_value=_mock_response([]))
        with pytest.raises(ValueError):
            await provider.get_current_weather("Fakecity")


class TestGetForecast:
    @pytest.mark.asyncio
    async def test_forecast_success(self, provider):
        responses = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(FORECAST_RESPONSE),
        ]
        provider.client.get = AsyncMock(side_effect=responses)

        result = await provider.get_forecast("Tokyo", days=2)
        assert result["city"] == "Tokyo"
        assert len(result["forecast"]) == 2
        day1 = result["forecast"][0]
        assert day1["date"] == "2026-03-05"
        assert day1["temp_high_f"] == 72.0
        assert day1["temp_low_f"] == 68.0
        assert day1["conditions"] == "sunny"

    @pytest.mark.asyncio
    async def test_forecast_single_day(self, provider):
        single_day_response = {
            "list": [
                {
                    "dt_txt": "2026-03-05 12:00:00",
                    "main": {"temp": 70.0, "humidity": 50},
                    "weather": [{"description": "rain"}],
                }
            ]
        }
        responses = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(single_day_response),
        ]
        provider.client.get = AsyncMock(side_effect=responses)

        result = await provider.get_forecast("Tokyo", days=1)
        assert len(result["forecast"]) == 1
        assert result["forecast"][0]["conditions"] == "rain"


class TestGetAirQuality:
    @pytest.mark.asyncio
    async def test_air_quality_success(self, provider):
        responses = [
            _mock_response(GEOCODE_RESPONSE),
            _mock_response(AIR_QUALITY_RESPONSE),
        ]
        provider.client.get = AsyncMock(side_effect=responses)

        result = await provider.get_air_quality("Tokyo")
        assert result["city"] == "Tokyo"
        assert result["aqi"] == 2
        assert result["aqi_label"] == "Fair"
        assert result["pm2_5"] == 12.5
        assert result["co"] == 230.0

import pytest
from unittest.mock import AsyncMock, MagicMock
from services.weather_service import WeatherService


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
def mock_provider():
    provider = MagicMock()
    provider.get_current_weather = AsyncMock(return_value=MOCK_CURRENT)
    provider.get_forecast = AsyncMock(return_value=MOCK_FORECAST)
    provider.get_air_quality = AsyncMock(return_value=MOCK_AIR)
    return provider


@pytest.fixture
def service(mock_provider):
    return WeatherService(provider=mock_provider)


class TestWeatherServiceDelegation:
    """Verify the service delegates to the provider."""

    @pytest.mark.asyncio
    async def test_get_current_weather_delegates(self, service, mock_provider):
        result, cached = await service.get_current_weather("Tokyo")
        assert result == MOCK_CURRENT
        assert cached is False
        mock_provider.get_current_weather.assert_called_once_with("Tokyo")

    @pytest.mark.asyncio
    async def test_get_forecast_delegates(self, service, mock_provider):
        result, cached = await service.get_forecast("Tokyo", days=3)
        assert result == MOCK_FORECAST
        assert cached is False
        mock_provider.get_forecast.assert_called_once_with("Tokyo", 3)

    @pytest.mark.asyncio
    async def test_get_air_quality_delegates(self, service, mock_provider):
        result, cached = await service.get_air_quality("Tokyo")
        assert result == MOCK_AIR
        assert cached is False
        mock_provider.get_air_quality.assert_called_once_with("Tokyo")


class TestWeatherServiceCaching:
    """Verify the caching layer prevents redundant provider calls."""

    @pytest.mark.asyncio
    async def test_second_call_uses_cache(self, service, mock_provider):
        _, cached1 = await service.get_current_weather("Tokyo")
        _, cached2 = await service.get_current_weather("Tokyo")
        assert cached1 is False
        assert cached2 is True
        assert mock_provider.get_current_weather.call_count == 1

    @pytest.mark.asyncio
    async def test_different_cities_both_call_provider(self, service, mock_provider):
        await service.get_current_weather("Tokyo")
        await service.get_current_weather("London")
        assert mock_provider.get_current_weather.call_count == 2

    @pytest.mark.asyncio
    async def test_forecast_cached_per_city_and_days(self, service, mock_provider):
        _, c1 = await service.get_forecast("Tokyo", days=3)
        _, c2 = await service.get_forecast("Tokyo", days=3)  # cache hit
        _, c3 = await service.get_forecast("Tokyo", days=5)  # different key
        assert c1 is False
        assert c2 is True
        assert c3 is False
        assert mock_provider.get_forecast.call_count == 2

    @pytest.mark.asyncio
    async def test_air_quality_cached(self, service, mock_provider):
        _, c1 = await service.get_air_quality("Tokyo")
        _, c2 = await service.get_air_quality("Tokyo")
        assert c1 is False
        assert c2 is True
        assert mock_provider.get_air_quality.call_count == 1

    @pytest.mark.asyncio
    async def test_cache_key_is_case_insensitive(self, service, mock_provider):
        _, c1 = await service.get_current_weather("Tokyo")
        _, c2 = await service.get_current_weather("tokyo")
        _, c3 = await service.get_current_weather("  TOKYO  ")
        assert c1 is False
        assert c2 is True
        assert c3 is True
        assert mock_provider.get_current_weather.call_count == 1

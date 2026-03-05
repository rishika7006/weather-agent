from abc import ABC, abstractmethod


class WeatherProvider(ABC):
    """Abstract base class that all weather providers must implement.

    Each method must return data in the standardized schema below so that
    the rest of the application is completely provider-agnostic.
    """

    @abstractmethod
    async def geocode(self, city: str) -> dict:
        """Convert a city name to coordinates.

        Returns:
            {"lat": float, "lon": float, "name": str, "country": str}
        """

    @abstractmethod
    async def get_current_weather(self, city: str) -> dict:
        """Fetch current weather conditions.

        Returns:
            {
                "city": str, "country": str,
                "temperature_f": float, "feels_like_f": float,
                "humidity": int, "description": str, "icon": str,
                "wind_speed_mph": float, "pressure_hpa": float,
                "visibility_m": int | str,
            }
        """

    @abstractmethod
    async def get_forecast(self, city: str, days: int = 3) -> dict:
        """Fetch multi-day forecast.

        Returns:
            {
                "city": str, "country": str,
                "forecast": [
                    {
                        "date": str, "temp_high_f": float, "temp_low_f": float,
                        "avg_humidity": float, "conditions": str,
                    }, ...
                ]
            }
        """

    @abstractmethod
    async def get_air_quality(self, city: str) -> dict:
        """Fetch air quality data.

        Returns:
            {
                "city": str, "country": str,
                "aqi": int, "aqi_label": str,
                "pm2_5": float, "pm10": float,
                "co": float, "no2": float, "o3": float,
            }
        """

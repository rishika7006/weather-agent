import httpx
from langchain_core.tools import tool
from config import MCP_SERVER_URL


@tool
def get_current_weather(city: str) -> str:
    """Get the current weather conditions for a city.

    Args:
        city: The name of the city (e.g., 'New York', 'London', 'Tokyo').

    Returns:
        A string with current weather data including temperature, humidity,
        wind speed, and conditions.
    """
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/api/weather/current", params={"city": city}, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()["data"]
        return (
            f"Current weather in {data['city']}, {data['country']}:\n"
            f"- Temperature: {data['temperature_f']}°F (feels like {data['feels_like_f']}°F)\n"
            f"- Conditions: {data['description']}\n"
            f"- Humidity: {data['humidity']}%\n"
            f"- Wind Speed: {data['wind_speed_mph']} mph\n"
            f"- Pressure: {data['pressure_hpa']} hPa\n"
            f"- Visibility: {data['visibility_m']}m"
        )
    except httpx.HTTPStatusError as e:
        return f"Error fetching weather for '{city}': {e.response.json().get('detail', str(e))}"
    except Exception as e:
        return f"Error connecting to weather service: {str(e)}"


@tool
def get_weather_forecast(city: str, days: int = 3) -> str:
    """Get a multi-day weather forecast for a city.

    Args:
        city: The name of the city (e.g., 'New York', 'London', 'Tokyo').
        days: Number of forecast days (1-5). Defaults to 3.

    Returns:
        A string with the daily forecast including high/low temps and conditions.
    """
    try:
        resp = httpx.get(
            f"{MCP_SERVER_URL}/api/weather/forecast",
            params={"city": city, "days": min(days, 5)},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        lines = [f"Weather forecast for {data['city']}, {data['country']}:"]
        for day in data["forecast"]:
            lines.append(
                f"- {day['date']}: High {day['temp_high_f']}°F, Low {day['temp_low_f']}°F, "
                f"{day['conditions']}, Humidity {day['avg_humidity']}%"
            )
        return "\n".join(lines)
    except httpx.HTTPStatusError as e:
        return f"Error fetching forecast for '{city}': {e.response.json().get('detail', str(e))}"
    except Exception as e:
        return f"Error connecting to weather service: {str(e)}"


@tool
def get_air_quality(city: str) -> str:
    """Get the air quality index (AQI) for a city.

    Args:
        city: The name of the city (e.g., 'New York', 'London', 'Tokyo').

    Returns:
        A string with the AQI rating and pollutant levels.
    """
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/api/weather/air-quality", params={"city": city}, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()["data"]
        return (
            f"Air quality in {data['city']}, {data['country']}:\n"
            f"- AQI: {data['aqi']} ({data['aqi_label']})\n"
            f"- PM2.5: {data['pm2_5']} μg/m³\n"
            f"- PM10: {data['pm10']} μg/m³\n"
            f"- Ozone (O₃): {data['o3']} μg/m³\n"
            f"- NO₂: {data['no2']} μg/m³\n"
            f"- CO: {data['co']} μg/m³"
        )
    except httpx.HTTPStatusError as e:
        return f"Error fetching air quality for '{city}': {e.response.json().get('detail', str(e))}"
    except Exception as e:
        return f"Error connecting to weather service: {str(e)}"


ALL_TOOLS = [get_current_weather, get_weather_forecast, get_air_quality]

import httpx
from langchain_core.tools import tool
from config import MCP_SERVER_URL
from direct_weather import get_direct_client

CACHED_MARKER = "\n[CACHED]"
FALLBACK_MARKER = "\n[FALLBACK]"

# Errors that indicate the MCP server itself is down (not a user/data error)
_MCP_DOWN_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, OSError)


def _is_server_error(exc: httpx.HTTPStatusError) -> bool:
    return exc.response.status_code >= 500


def _format_current(data: dict) -> str:
    return (
        f"Current weather in {data['city']}, {data['country']}:\n"
        f"- Temperature: {data['temperature_f']}\u00b0F (feels like {data['feels_like_f']}\u00b0F)\n"
        f"- Conditions: {data['description']}\n"
        f"- Humidity: {data['humidity']}%\n"
        f"- Wind Speed: {data['wind_speed_mph']} mph\n"
        f"- Pressure: {data['pressure_hpa']} hPa\n"
        f"- Visibility: {data['visibility_m']}m"
    )


def _format_forecast(data: dict) -> str:
    lines = [f"Weather forecast for {data['city']}, {data['country']}:"]
    for day in data["forecast"]:
        lines.append(
            f"- {day['date']}: High {day['temp_high_f']}\u00b0F, Low {day['temp_low_f']}\u00b0F, "
            f"{day['conditions']}, Humidity {day['avg_humidity']}%"
        )
    return "\n".join(lines)


def _format_air_quality(data: dict) -> str:
    return (
        f"Air quality in {data['city']}, {data['country']}:\n"
        f"- AQI: {data['aqi']} ({data['aqi_label']})\n"
        f"- PM2.5: {data['pm2_5']} \u03bcg/m\u00b3\n"
        f"- PM10: {data['pm10']} \u03bcg/m\u00b3\n"
        f"- Ozone (O\u2083): {data['o3']} \u03bcg/m\u00b3\n"
        f"- NO\u2082: {data['no2']} \u03bcg/m\u00b3\n"
        f"- CO: {data['co']} \u03bcg/m\u00b3"
    )


@tool
def get_current_weather(city: str) -> str:
    """Get the current weather conditions for a city.

    Args:
        city: The name of the city (e.g., 'New York', 'London', 'Tokyo').

    Returns:
        A string with current weather data including temperature, humidity,
        wind speed, and conditions.
    """
    # Try MCP server first
    try:
        resp = httpx.get(f"{MCP_SERVER_URL}/api/weather/current", params={"city": city}, timeout=10.0)
        resp.raise_for_status()
        body = resp.json()
        result = _format_current(body["data"])
        if body.get("cached"):
            result += CACHED_MARKER
        return result
    except httpx.HTTPStatusError as e:
        if not _is_server_error(e):
            return f"Error fetching weather for '{city}': {e.response.json().get('detail', str(e))}"
        # Server error — fall through to fallback
    except _MCP_DOWN_ERRORS:
        pass  # MCP server unreachable — fall through to fallback
    except Exception as e:
        # Unexpected error from MCP — still try fallback
        pass

    # Fallback: call OpenWeatherMap directly
    try:
        client = get_direct_client()
        data = client.get_current_weather(city)
        return _format_current(data) + FALLBACK_MARKER
    except ValueError as e:
        return str(e)
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
        body = resp.json()
        result = _format_forecast(body["data"])
        if body.get("cached"):
            result += CACHED_MARKER
        return result
    except httpx.HTTPStatusError as e:
        if not _is_server_error(e):
            return f"Error fetching forecast for '{city}': {e.response.json().get('detail', str(e))}"
    except _MCP_DOWN_ERRORS:
        pass
    except Exception:
        pass

    try:
        client = get_direct_client()
        data = client.get_forecast(city, min(days, 5))
        return _format_forecast(data) + FALLBACK_MARKER
    except ValueError as e:
        return str(e)
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
        body = resp.json()
        result = _format_air_quality(body["data"])
        if body.get("cached"):
            result += CACHED_MARKER
        return result
    except httpx.HTTPStatusError as e:
        if not _is_server_error(e):
            return f"Error fetching air quality for '{city}': {e.response.json().get('detail', str(e))}"
    except _MCP_DOWN_ERRORS:
        pass
    except Exception:
        pass

    try:
        client = get_direct_client()
        data = client.get_air_quality(city)
        return _format_air_quality(data) + FALLBACK_MARKER
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error connecting to weather service: {str(e)}"


ALL_TOOLS = [get_current_weather, get_weather_forecast, get_air_quality]

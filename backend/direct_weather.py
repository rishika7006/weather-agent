import httpx
from config import OPENWEATHER_API_KEY

BASE_URL = "https://api.openweathermap.org"


class DirectWeatherClient:
    """Lightweight fallback client that calls OpenWeatherMap directly,
    bypassing the MCP server. Used when the MCP server is unreachable."""

    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY

    def _geocode(self, city: str) -> dict:
        resp = httpx.get(
            f"{BASE_URL}/geo/1.0/direct",
            params={"q": city, "limit": 1, "appid": self.api_key},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError(f"City '{city}' not found.")
        return {
            "lat": data[0]["lat"],
            "lon": data[0]["lon"],
            "name": data[0].get("name", city),
            "country": data[0].get("country", ""),
        }

    def get_current_weather(self, city: str) -> dict:
        geo = self._geocode(city)
        resp = httpx.get(
            f"{BASE_URL}/data/2.5/weather",
            params={"lat": geo["lat"], "lon": geo["lon"],
                    "appid": self.api_key, "units": "imperial"},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "city": geo["name"], "country": geo["country"],
            "temperature_f": data["main"]["temp"],
            "feels_like_f": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed_mph": data["wind"]["speed"],
            "pressure_hpa": data["main"]["pressure"],
            "visibility_m": data.get("visibility", "N/A"),
        }

    def get_forecast(self, city: str, days: int = 3) -> dict:
        geo = self._geocode(city)
        resp = httpx.get(
            f"{BASE_URL}/data/2.5/forecast",
            params={"lat": geo["lat"], "lon": geo["lon"],
                    "appid": self.api_key, "units": "imperial",
                    "cnt": min(days, 5) * 8},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

        daily = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {"date": date, "temps": [], "descriptions": [], "humidity": []}
            daily[date]["temps"].append(entry["main"]["temp"])
            daily[date]["descriptions"].append(entry["weather"][0]["description"])
            daily[date]["humidity"].append(entry["main"]["humidity"])

        forecast_days = []
        for date, info in list(daily.items())[:days]:
            forecast_days.append({
                "date": info["date"],
                "temp_high_f": round(max(info["temps"]), 1),
                "temp_low_f": round(min(info["temps"]), 1),
                "avg_humidity": round(sum(info["humidity"]) / len(info["humidity"]), 1),
                "conditions": max(set(info["descriptions"]), key=info["descriptions"].count),
            })

        return {"city": geo["name"], "country": geo["country"], "forecast": forecast_days}

    def get_air_quality(self, city: str) -> dict:
        geo = self._geocode(city)
        resp = httpx.get(
            f"{BASE_URL}/data/2.5/air_pollution",
            params={"lat": geo["lat"], "lon": geo["lon"], "appid": self.api_key},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        aqi = data["list"][0]["main"]["aqi"]
        components = data["list"][0]["components"]
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        return {
            "city": geo["name"], "country": geo["country"],
            "aqi": aqi, "aqi_label": aqi_labels.get(aqi, "Unknown"),
            "pm2_5": components.get("pm2_5"), "pm10": components.get("pm10"),
            "co": components.get("co"), "no2": components.get("no2"),
            "o3": components.get("o3"),
        }


# Singleton — only created once, reused across tool calls
_client = None


def get_direct_client() -> DirectWeatherClient:
    global _client
    if _client is None:
        _client = DirectWeatherClient()
    return _client

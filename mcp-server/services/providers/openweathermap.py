import httpx
from services.providers.base import WeatherProvider


class OpenWeatherMapProvider(WeatherProvider):
    """Weather provider backed by the OpenWeatherMap API."""

    def __init__(self, api_key: str, base_url: str = "https://api.openweathermap.org"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def geocode(self, city: str) -> dict:
        url = f"{self.base_url}/geo/1.0/direct"
        params = {"q": city, "limit": 1, "appid": self.api_key}
        resp = await self.client.get(url, params=params)
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

    async def get_current_weather(self, city: str) -> dict:
        geo = await self.geocode(city)
        url = f"{self.base_url}/data/2.5/weather"
        params = {
            "lat": geo["lat"],
            "lon": geo["lon"],
            "appid": self.api_key,
            "units": "imperial",
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        return {
            "city": geo["name"],
            "country": geo["country"],
            "temperature_f": data["main"]["temp"],
            "feels_like_f": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed_mph": data["wind"]["speed"],
            "pressure_hpa": data["main"]["pressure"],
            "visibility_m": data.get("visibility", "N/A"),
        }

    async def get_forecast(self, city: str, days: int = 3) -> dict:
        geo = await self.geocode(city)
        url = f"{self.base_url}/data/2.5/forecast"
        params = {
            "lat": geo["lat"],
            "lon": geo["lon"],
            "appid": self.api_key,
            "units": "imperial",
            "cnt": min(days, 5) * 8,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        daily = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "temps": [],
                    "descriptions": [],
                    "humidity": [],
                }
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

        return {
            "city": geo["name"],
            "country": geo["country"],
            "forecast": forecast_days,
        }

    async def get_air_quality(self, city: str) -> dict:
        geo = await self.geocode(city)
        url = f"{self.base_url}/data/2.5/air_pollution"
        params = {
            "lat": geo["lat"],
            "lon": geo["lon"],
            "appid": self.api_key,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        aqi = data["list"][0]["main"]["aqi"]
        components = data["list"][0]["components"]
        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

        return {
            "city": geo["name"],
            "country": geo["country"],
            "aqi": aqi,
            "aqi_label": aqi_labels.get(aqi, "Unknown"),
            "pm2_5": components.get("pm2_5"),
            "pm10": components.get("pm10"),
            "co": components.get("co"),
            "no2": components.get("no2"),
            "o3": components.get("o3"),
        }

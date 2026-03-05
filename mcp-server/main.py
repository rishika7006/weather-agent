import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from config import WEATHER_PROVIDER, OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL
from services.weather_service import WeatherService

app = FastAPI(
    title="Weather MCP Server",
    description="Microservice wrapper for weather APIs",
    version="1.0.0",
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)


def create_weather_service() -> WeatherService:
    """Factory that instantiates the configured weather provider."""
    if WEATHER_PROVIDER == "openweathermap":
        from services.providers.openweathermap import OpenWeatherMapProvider
        provider = OpenWeatherMapProvider(
            api_key=OPENWEATHER_API_KEY,
            base_url=OPENWEATHER_BASE_URL,
        )
    else:
        raise ValueError(
            f"Unknown WEATHER_PROVIDER: '{WEATHER_PROVIDER}'. "
            f"Supported providers: openweathermap"
        )
    return WeatherService(provider=provider)


weather_service = create_weather_service()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-server", "provider": WEATHER_PROVIDER}


@app.get("/api/cache/stats")
async def cache_stats():
    """Get LFU cache statistics."""
    return {"success": True, "data": weather_service.cache.stats()}


@app.get("/api/weather/current")
async def get_current_weather(city: str = Query(..., min_length=1, max_length=100, description="City name (e.g., 'New York', 'London')")):
    """Get current weather conditions for a city."""
    try:
        result, cached = await weather_service.get_current_weather(city)
        return {"success": True, "data": result, "cached": cached}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Weather service error. Please try again.")


@app.get("/api/weather/forecast")
async def get_weather_forecast(
    city: str = Query(..., min_length=1, max_length=100, description="City name"),
    days: int = Query(3, ge=1, le=5, description="Number of forecast days (1-5)"),
):
    """Get multi-day weather forecast for a city."""
    try:
        result, cached = await weather_service.get_forecast(city, days)
        return {"success": True, "data": result, "cached": cached}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Weather service error. Please try again.")


@app.get("/api/weather/air-quality")
async def get_air_quality(city: str = Query(..., min_length=1, max_length=100, description="City name")):
    """Get air quality index for a city."""
    try:
        result, cached = await weather_service.get_air_quality(city)
        return {"success": True, "data": result, "cached": cached}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Weather service error. Please try again.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

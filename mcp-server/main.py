from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from services.weather_service import WeatherService

app = FastAPI(
    title="Weather MCP Server",
    description="Microservice wrapper for OpenWeatherMap API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_service = WeatherService()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-server"}


@app.get("/api/weather/current")
async def get_current_weather(city: str = Query(..., description="City name (e.g., 'New York', 'London')")):
    """Get current weather conditions for a city."""
    try:
        result = await weather_service.get_current_weather(city)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@app.get("/api/weather/forecast")
async def get_weather_forecast(
    city: str = Query(..., description="City name"),
    days: int = Query(3, ge=1, le=5, description="Number of forecast days (1-5)"),
):
    """Get multi-day weather forecast for a city."""
    try:
        result = await weather_service.get_forecast(city, days)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@app.get("/api/weather/air-quality")
async def get_air_quality(city: str = Query(..., description="City name")):
    """Get air quality index for a city."""
    try:
        result = await weather_service.get_air_quality(city)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

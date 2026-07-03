import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import httpx

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from services.weather import get_coordinates, get_weather, WeatherDay
from services.places import get_attractions, Place

app = FastAPI(title="Smart Travel Dashboard API")

# Папка для статики (HTML, CSS, JS)
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)


def serialize_weather(day: WeatherDay) -> dict:
    return {
        "date": day.date,
        "temperature_c": day.temperature_c,
        "formatted_temperature": day.formatted_temperature,
        "formatted_precipitation": day.formatted_precipitation,
        "formatted_wind": day.formatted_wind,
    }


def serialize_place(place: Place) -> dict:
    return {
        "name": place.name,
        "rating": place.rating,
        "reviews_count": place.reviews_count,
        "description": place.description,
    }


@app.get("/api/travel")
async def get_travel_data(city: str = Query("Kyiv", description="Назва міста англійською")):
    today = datetime.now().date()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            coord = await get_coordinates(client, city)
            weather_task = get_weather(client, coord, start_date, end_date)
            places_task = get_attractions(client, city)

            weather_days, places = await asyncio.gather(weather_task, places_task)

            return {
                "status": "success",
                "city": city,
                "start_date": start_date,
                "end_date": end_date,
                "weather": [serialize_weather(w) for w in weather_days],
                "places": [serialize_place(p) for p in places],
            }
        except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка отримання даних: {str(e)}")


@app.get("/")
async def read_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return {"message": "Файл index.html не знайдено в теці static/"}
    return FileResponse(index_file)


# Підключаємо роздачу статики
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

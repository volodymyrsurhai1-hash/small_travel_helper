from dataclasses import dataclass
from services.interfaces import AsyncHttpClient

import asyncio
import httpx



WIND_MODERATE_KMH = 10.0
WIND_STRONG_KMH = 20.0
PRECIPITATION_RAIN_MM = 2.0


@dataclass(frozen=True)
class Coord:
    lon: float
    lat: float


@dataclass(frozen=True)
class WeatherDay:
    date: str
    temperature_c: float
    precipitation_mm: float         
    wind_speed_kmh: float

    @property
    def formatted_temperature(self) -> str:
        return f"+{self.temperature_c}°C" if self.temperature_c > 0 else f"{self.temperature_c}°C"

    @property
    def formatted_precipitation(self) -> str:
        if self.precipitation_mm == 0:
            return "Сухо"
        elif self.precipitation_mm < PRECIPITATION_RAIN_MM:
            return f"Моросить ({self.precipitation_mm} мм)"
        return f"Дощ ({self.precipitation_mm} мм)"

    @property
    def formatted_wind(self) -> str:
        if self.wind_speed_kmh < WIND_MODERATE_KMH:
            return f"Слабкий вітер ({self.wind_speed_kmh} км/год)"
        elif self.wind_speed_kmh < WIND_STRONG_KMH:
            return f"Помірний вітер ({self.wind_speed_kmh} км/год)"
        return f"Сильний вітер ({self.wind_speed_kmh} км/год)"

    def __str__(self) -> str:
        # Створюємо гарний вивід для print(weather_day)
        return f"WeatherDay(date='{self.date}', temp={self.formatted_temperature}, prec='{self.formatted_precipitation}', wind='{self.formatted_wind}')"


async def get_coordinates(client: AsyncHttpClient, city: str) -> Coord:
    """Getting coordinates from Weather API"""
    response = await client.get(
        f'https://geocoding-api.open-meteo.com/v1/search',
        params={
            'name': city,
            'count': 1,
            'format': 'json'
        }
    )

    response.raise_for_status()
    data = response.json()
    
    if not data.get('results'):
        raise ValueError(f"Місто '{city}' не знайдено")

    city_data = data['results'][0]
    return Coord(city_data['longitude'], city_data['latitude'])


def aggregate_weather_by_days(weather_data: dict) -> list[WeatherDay]:
    """
    Aggregate weather by days
    """
    daily_data = weather_data.get("daily", {})
    if not daily_data:
        return []
        
    result = []
    
    for date, temp, prec, wind in zip(
        daily_data.get("time", []), 
        daily_data.get("temperature_2m_mean", []), 
        daily_data.get("precipitation_sum", []),
        daily_data.get("wind_speed_10m_max", [])
    ):
        result.append(WeatherDay(
            date=date,
            temperature_c=float(temp),
            precipitation_mm=float(prec),
            wind_speed_kmh=float(wind)
        ))
        
    return result


async def get_weather(client: AsyncHttpClient, coord: Coord, start_date: str, end_date: str) -> list[WeatherDay]:
    """Getting weather"""
    response = await client.get(
        f'https://api.open-meteo.com/v1/forecast',
        params={
            'latitude': coord.lat,
            'longitude': coord.lon,
            'daily': 'temperature_2m_mean,precipitation_sum,wind_speed_10m_max',
            'timezone': 'auto',
            'start_date': start_date, 
            'end_date': end_date    
        }
    )

    response.raise_for_status()
    
    return aggregate_weather_by_days(response.json())


async def main():
    # Створюємо один клієнт на всі запити (Best Practice)
    async with httpx.AsyncClient(timeout=10.0) as client:
        coord = await get_coordinates(client, "Kyiv")
        nice_weather = await get_weather(client, coord, "2026-06-15", "2026-06-20")
        
        for day in nice_weather:
            print(day)

if __name__ == "__main__":
    # Запуск асинхронного event loop
    asyncio.run(main())
import asyncio
import httpx
from datetime import datetime, timedelta

from services.weather import get_coordinates, get_weather
from services.places import get_attractions


async def run_travel_etl(city: str) -> None:
    print(f"\n🌍 Збираємо дані для міста: {city}...")
    
    # Розрахуємо дати на найближчі 5 днів
    today = datetime.now().date()
    start_date = today.strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            # 1. Отримуємо координати міста для погоди
            coord = await get_coordinates(client, city)
            
            # 2. Паралельно запускаємо запит на погоду і на пам'ятки через asyncio.gather
            weather_task = get_weather(client, coord, start_date, end_date)
            places_task = get_attractions(client, city)
            
            weather_days, places = await asyncio.gather(weather_task, places_task)
            
            # --- ВИВІД ЗВІТУ ---
            print("\n" + "="*50)
            print(f"🌤 ПОГОДА У МІСТІ {city.upper()} ({start_date} — {end_date})")
            print("="*50)
            for day in weather_days:
                print(f" • {day.date}: {day.formatted_temperature} | {day.formatted_precipitation} | {day.formatted_wind}")
                
            print("\n" + "="*50)
            print(f"🏛 ТОП-10 ПАМ'ЯТОК (за рейтингом та відгуками)")
            print("="*50)
            for idx, place in enumerate(places, 1):
                print(f" {idx}. {place.name} — ⭐ {place.rating} ({place.reviews_count} відгуків)")
                print(f"    📝 {place.description}")
                
        except Exception as e:
            print(f"❌ Помилка при отриманні даних: {e}")


async def main():
    city = input("Введіть назву міста англійською (наприклад, Kyiv, Lviv, Odesa) [за замовчуванням Kyiv]: ").strip()
    if not city:
        city = "Kyiv"
    await run_travel_etl(city)


if __name__ == "__main__":
    asyncio.run(main())

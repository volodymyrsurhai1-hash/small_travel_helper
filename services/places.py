import httpx
from dataclasses import dataclass
import config
from services.interfaces import AsyncHttpClient

SERPAPI_KEY = config.SERPAPI_KEY

@dataclass(frozen=True)
class Place:
    name: str
    rating: float
    reviews_count: int
    description: str

async def get_attractions(client: AsyncHttpClient, city: str) -> list[Place]:
    """ Getting places from Google Local API"""
    params = {
        "engine": "google_local",
        "q": f"достопримечательности {city}",
        "api_key": SERPAPI_KEY,
        "hl": "uk",  # Язык результатов
    }
    
    response = await client.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()
    
    places = []
    results = data.get("local_results", [])
    
    for item in results:
        # У Google Local буває, що немає description, тому використовуємо .get() і фолбек
        desc = item.get("description") or item.get("type", "Без опису")
        
        places.append(Place(
            name=item.get("title", "Невідома локація"),
            rating=float(item.get("rating", 0.0)),
            reviews_count=int(item.get("reviews", 0)),
            description=desc
        ))
        
    # Сортуємо спочатку за рейтингом, а при рівному рейтингу — за кількістю відгуків (за спаданням)
    places.sort(key=lambda p: (p.rating, p.reviews_count), reverse=True)
    
    return places[:10]
    
async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Для тесту шукаємо пам'ятки в Києві
        data = await get_attractions(client, "Kyiv")
        print(data)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

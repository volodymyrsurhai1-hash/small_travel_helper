from typing import Protocol, Any

class AsyncHttpClient(Protocol):
    """
    Абстрактний інтерфейс HTTP-клієнта.
    Будь-який клієнт (httpx, aiohttp, mock), який має асинхронний метод get, 
    підійде для використання у наших сервісах.
    """
    async def get(self, *args: Any, **kwargs: Any) -> Any: ...






FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Копіюємо файли залежностей для кешування шарів Docker
COPY pyproject.toml uv.lock ./

# Встановлюємо залежності без створення віртуального середовища всередині контейнера
RUN uv sync --frozen --no-dev

# Копіюємо вихідний код додатку
COPY . .

# Відкриваємо порт
EXPOSE 8000

# Запускаємо Uvicorn сервер
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

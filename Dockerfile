# 1. Беремо легкий образ Python
FROM python:3.11-slim

# 2. Вимикаємо кешування байткоду (щоб не смітити)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Робоча папка всередині контейнера
WORKDIR /app

# 4. Копіюємо файл із залежностями
COPY requirements.txt .

# 5. Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо весь наш код у контейнер
COPY . .

# 7. Відкриваємо порт (для інформації)
EXPOSE 8000

# 8. Команда запуску сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 🚀 Task Analytics Microservice

Асинхронний REST API для управління задачами та збору статистики користувачів.
Проєкт розроблено з використанням сучасного стеку Python (FastAPI, SQLAlchemy 2.0) та практик DevOps.

## 🛠 Технологічний стек
- **Core:** Python 3.11, FastAPI, Pydantic
- **Database:** PostgreSQL, SQLAlchemy (Async), Alembic (Migrations)
- **Testing:** Pytest, AsyncIO (Integration Tests)
- **Infrastructure:** Docker, Docker Compose
- **CI/CD:** GitHub Actions (Automated Testing)
- **Deployment:** Render.com (Cloud)

## 🔥 Функціонал
- **CRUD** операції для користувачів та задач.
- **PATCH** оновлення статусу виконання задачі.
- **Analytics Endpoint:** розрахунок Completion Rate для користувача (SQL Aggregation).
- **Dependency Injection** для управління сесіями БД.

## ⚙️ Як запустити локально
1. Клонуйте репозиторій:
   ```bash
   git clone [https://github.com/RomasYurii/Docker-fastapi-project.git](https://github.com/RomasYurii/Docker-fastapi-project.git)
2. Створіть файл .env (приклад у .env.example).
3. Запустіть через Docker Compose:
    ```bash
     docker-compose up -d --build
4. Документація доступна за адресою: http://localhost:8000/docs
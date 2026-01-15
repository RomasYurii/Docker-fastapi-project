import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from main import app, get_db  # Імпортуємо наш додаток
from relational_db import Base  # Імпортуємо моделі для створення таблиць

# 1. НАЛАШТУВАННЯ ТЕСТОВОЇ БАЗИ (SQLite в пам'яті)
# Використовуємо SQLite, бо це миттєво і не треба окремого Докера
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Магія: тримає базу в пам'яті живою між запитами
)
TestingSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


# 2. ФІКСТУРА (Підготовка середовища перед кожним тестом)
@pytest.fixture(scope="function")
async def db_session():
    # Створюємо таблиці
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Створюємо сесію
    async with TestingSessionLocal() as session:
        yield session

    # Видаляємо таблиці після тесту (чистота)
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 3. OVERRIDE (Підміна реальної бази на тестову)
@pytest.fixture(scope="function")
async def client(db_session):
    # Функція-замінник, яка видасть нашу тестову сесію
    async def override_get_db():
        yield db_session

    # Підміняємо залежність
    app.dependency_overrides[get_db] = override_get_db

    # Створюємо клієнта (це наш "браузер" для тестів)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    # Прибираємо підміну після тесту
    app.dependency_overrides.clear()


# --- САМІ ТЕСТИ ---

@pytest.mark.asyncio
async def test_create_user(client):
    """Тест: Чи можемо ми створити юзера?"""
    response = await client.post("/users/", json={"username": "tester"})

    # Перевірки (Asserts)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tester"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_for_user(client):
    """Тест: Створити юзера, а потім задачу для нього"""
    # 1. Створюємо юзера
    resp_user = await client.post("/users/", json={"username": "romas"})
    user_id = resp_user.json()["id"]

    # 2. Створюємо задачу, прив'язану до цього ID
    resp_task = await client.post("/tasks/", json={
        "name": "Write Pytest",
        "is_completed": False,  # У JSON це false (з маленької)
        "user_id": user_id
    })

    # 3. Перевіряємо
    assert resp_task.status_code == 200
    task_data = resp_task.json()
    assert task_data["name"] == "Write Pytest"
    assert task_data["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_task_no_user_fail(client):
    """Тест: Має бути помилка, якщо юзера не існує"""
    response = await client.post("/tasks/", json={
        "name": "Ghost Task",
        "user_id": 9999  # Такого юзера немає
    })

    assert response.status_code == 404
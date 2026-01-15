import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from main import app, get_db
from relational_db import Base


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)



@pytest.fixture(scope="function")
async def db_session():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/users/", json={"username": "tester"})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tester"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_for_user(client):
    resp_user = await client.post("/users/", json={"username": "romas"})
    user_id = resp_user.json()["id"]

    resp_task = await client.post("/tasks/", json={
        "name": "Write Pytest",
        "is_completed": False,
        "user_id": user_id
    })

    assert resp_task.status_code == 200
    task_data = resp_task.json()
    assert task_data["name"] == "Write Pytest"
    assert task_data["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_task_no_user_fail(client):
    response = await client.post("/tasks/", json={
        "name": "Ghost Task",
        "user_id": 9999
    })

    assert response.status_code == 404
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean,ForeignKey, select
from sqlalchemy import func, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
import os
from dotenv import load_dotenv

from models import *

# <--- Імпорт
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 1. КОНФІГУРАЦІЯ (Драйвер asyncpg)
# Зверни увагу: порт 5433 (твій Docker)
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Створюємо асинхронний двигун
engine = create_async_engine(DATABASE_URL, echo=False)

# Фабрика сесій (щоб щоразу не писати руками)
async_session = async_sessionmaker(engine, expire_on_commit=False)



async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def add_user(name: str):
    async with async_session() as session:
        new_user = User(username=name)
        session.add(new_user)
        await session.commit()
        print(f"➕ Додано: {name}")

async def get_user_and_tasks(name: str):
    async with async_session() as session:
        stmt = select(User).where(User.username == name).options(selectinload(User.tasks))

        result = await session.execute(stmt)
        user_from_db = result.scalar_one()

        print(f"Юзер: {user_from_db.username}")
        print(f"Його задачі: {user_from_db.tasks}")


async def add_task(name: str, user_id: int):
    """Додавання (INSERT)"""
    async with async_session() as session:
        new_task = Task(name=name, user_id=user_id)
        session.add(new_task)
        await session.commit()
        print(f"➕ Додано: {name}")

async def main():
    # 1. Ініціалізуємо базу
    await init_db()

    await add_user("Anton")

    await add_task("111", user_id=1)
    await add_task("222", user_id=1)

    await get_user_and_tasks("Anton")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
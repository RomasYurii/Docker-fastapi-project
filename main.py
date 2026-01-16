from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from relational_db import async_session, init_db, Task, User
import schemas, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
app = FastAPI(title="Task Queue API")


async def get_db():
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Якщо змінна "TESTING" не встановлена, тоді підключаємось до бази
    if os.getenv("TESTING") != "True":
        await init_db()
        print("🚀 База даних ініціалізована!")
    else:
        print("⚠️ Режим тестування: Пропускаємо підключення до Postgres")

    yield

    if os.getenv("TESTING") != "True":
        print("🛑 Додаток зупинено")


@app.post("/users/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    new_user = User(username=user.username)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail="User already exists")



@app.post("/tasks/", response_model=schemas.TaskRead)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(get_db)):
    """ Create a new task """
    user = await db.get(User, task.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_task = Task(
        name=task.name,
        is_completed=task.is_completed,
        user_id=task.user_id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


@app.get("/tasks/", response_model=list[schemas.TaskRead])
async def read_tasks(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Get all tasks"""
    result = await db.execute(select(Task).offset(skip).limit(limit))
    return result.scalars().all()


@app.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
async def update_task_status(task_id: int, is_completed: bool, db: AsyncSession = Depends(get_db)):
    """Update a task"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_completed = is_completed
    await db.commit()
    await db.refresh(task)

    return task


@app.get("/users/{user_id}/stats", response_model=schemas.UserStats)
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user stats"""

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total = await db.scalar(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    )

    completed = await db.scalar(
        select(func.count(Task.id)).where(Task.user_id == user_id, Task.is_completed == True)
    )

    rate = (completed / total * 100) if total > 0 else 0.0

    return {
        "user_id": user_id,
        "total_tasks": total or 0,
        "completed_tasks": completed or 0,
        "completion_rate": round(rate, 2)
    }
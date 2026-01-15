from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from relational_db import async_session, init_db, Task, User
import schemas

app = FastAPI(title="Task Queue API")


async def get_db():
    async with async_session() as session:
        yield session


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/users/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
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
    result = await db.execute(select(Task).offset(skip).limit(limit))
    return result.scalars().all()
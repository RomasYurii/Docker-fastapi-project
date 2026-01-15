from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func
from typing import List


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(60), unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    # Зв'язок
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<Task {self.id}: {self.name}>"
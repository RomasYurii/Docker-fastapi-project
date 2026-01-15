from pydantic import BaseModel, ConfigDict

# --- USERS ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    username: str

class UserRead(UserBase):
    id: int
    # Дозволяємо читати дані прямо з ORM об'єктів
    model_config = ConfigDict(from_attributes=True)




# --- TASKS ---
class TaskBase(BaseModel):
    name: str
    is_completed: bool = False

class TaskCreate(TaskBase):
    user_id: int

class TaskRead(TaskBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role: str


class UserLogin(BaseModel):
    username: str
    password: str


class UpdateSafetySetting(BaseModel):
    category: str
    method: str
    threshold: str

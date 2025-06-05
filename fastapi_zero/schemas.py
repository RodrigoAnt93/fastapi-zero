from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class UserInDB(User):
    id: int


class UserList(BaseModel):
    users: list[UserResponse]

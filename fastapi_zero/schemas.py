from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class User(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    id: int


class UserList(BaseModel):
    users: list[UserResponse]


class Token(BaseModel):
    access_token: str
    token_type: str

class FilterPages(BaseModel):
    limit: int = Field(default=10, ge=1)
    offset: int = Field(default=0, ge=0)
from pydantic import BaseModel, EmailStr, constr

class UserRegisterSchema(BaseModel):
    username: constr(min_length=3, max_length=80)
    email: EmailStr
    password: constr(min_length=6)

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class CollectionSchema(BaseModel):
    name: constr(min_length=1, max_length=100)
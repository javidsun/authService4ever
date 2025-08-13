from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class MeOut(BaseModel):
    id: str
    email: EmailStr
    is_email_verified: bool
    is_active: bool

class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

class EmailIn(BaseModel):
    email: EmailStr

class TokenIn(BaseModel):
    token: str

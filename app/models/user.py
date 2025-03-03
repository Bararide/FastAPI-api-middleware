from pydantic import Field
from pydantic import BaseModel, EmailStr, Field, validator


class RegisterUserRequest(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4)
    copy_password: str = Field(..., min_length=4)
    phone: str = Field(..., min_length=13)
    email: EmailStr

    @validator("copy_password")
    def passwords_match(cls, v, values):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

from pydantic import BaseModel, EmailStr, Field, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str
 
    
class RegisterRequest(BaseModel):
    first_name: str = Field(
        min_length=1,
        max_length=100,
    )
    last_name: str = Field(
        min_length=1,
        max_length=100,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class RegisterResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
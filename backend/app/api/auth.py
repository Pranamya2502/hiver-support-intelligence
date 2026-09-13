from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(request: LoginRequest):
    if request.email == "admin@hiver.com" and request.password == "hiver123":
        return {
            "access_token": "demo-token",
            "token_type": "bearer",
            "user": {
                "email": request.email,
                "name": "Hiver Admin",
            },
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid email or password",
    )
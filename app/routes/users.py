from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from app.RabbitMQ.MessagePublisher import MessagePublisher
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from app.models.user import RegisterUserRequest
from app.tokens.TokenManager import TokenManager

router = APIRouter()
message_publisher = MessagePublisher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/{id}")
async def get_user_by_id(id: int, token: Optional[str] = Header(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    token_data = TokenManager.validate_token(token)
    return await message_publisher.process_request(
        "get_user_by_id", "user_updates", "user_updates_response", id
    )


@router.post("/register")
async def register_user(
    user: RegisterUserRequest, client_token: Optional[str] = Header(None)
):
    """
    Регистрация нового пользователя:
    - Если передан токен, используется информация из токена для назначения роли.
    - Если токен не передан, пользователь регистрируется с базовой ролью user.
    """
    role = "user"

    if client_token:
        token_data = TokenManager.validate_token(client_token)
        role = token_data.get("role")
        if not role:
            raise HTTPException(status_code=400, detail="Invalid client token")

    return await message_publisher.process_request(
        "add_user_with_role",
        "user_updates",
        "user_updates_response",
        {
            "fullname": user.fullname,
            "password": user.password,
            "email": user.email,
            "phone": user.phone,
            "role": role,
        },
    )


@router.post("/generate-token")
async def generate_token(role: str):
    """
    Генерирует JWT токен с заданной ролью.

    Args:
        role (str): Роль, которую необходимо указать в токене.

    Returns:
        dict: Сгенерированный токен.
    """
    if role not in ["user", "admin", "moderator"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Allowed roles: user, admin, moderator",
        )
    token = TokenManager.create_admin_token(role)
    return {"token": token}


import json


@router.post("/login")
async def login(user: RegisterUserRequest):
    user_data = await message_publisher.process_request(
        "get_user",
        "user_updates",
        "user_updates_response",
        {"password": user.password, "email": user.email, "phone": user.phone},
    )

    print(user_data)

    parsed_data = json.loads(user_data["data"])

    if not parsed_data or parsed_data.get("password") != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = parsed_data.get("role", "user")

    access_token = TokenManager.create_access_token(
        {
            "email": user.email,
            "password": user.password,
            "phone": user.phone,
            "role": role,
        }
    )
    refresh_token = TokenManager.create_refresh_token(
        {
            "email": user.email,
            "password": user.password,
            "phone": user.phone,
        }
    )

    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )
    return response


@router.post("/refresh")
async def refresh_token(refresh_token: Optional[str] = Header(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is missing")

    try:
        payload = TokenManager.validate_token(refresh_token)
        user_email = payload.get("sub")
        user_role = payload.get("role")

        if not user_email or not user_role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        new_access_token = TokenManager.create_access_token(
            {"sub": user_email, "role": user_role}
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = TokenManager.validate_token(token)
        user_role = payload.get("role")
        return {"message": f"Welcome, {user_role}"}
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid access token")

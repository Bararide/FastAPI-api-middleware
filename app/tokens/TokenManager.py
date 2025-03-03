import jwt
import json

from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Header

from app.RabbitMQ.MessagePublisher import MessagePublisher

messagePublisher = MessagePublisher()


class TokenManager:
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    @staticmethod
    def create_admin_token(role: str, email: str, password: str, phone: str) -> str:
        """
        Создает токен с информацией о роли, email, password и phone.
        """
        to_encode = {
            "role": role,
            "email": email,
            "password": password,
            "phone": phone,
            "issued_at": datetime.utcnow().isoformat(),
        }

        expire = datetime.utcnow() + timedelta(
            minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, TokenManager.SECRET_KEY, algorithm=TokenManager.ALGORITHM
        )

    @staticmethod
    def validate_token(token: str) -> dict:
        """
        Проверяет токен на валидность.
        """
        try:
            payload = jwt.decode(
                token, TokenManager.SECRET_KEY, algorithms=[TokenManager.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Создает короткоживущий Access-токен.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, TokenManager.SECRET_KEY, algorithm=TokenManager.ALGORITHM
        )

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Создает долгоиграющий Refresh-токен.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            days=TokenManager.REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, TokenManager.SECRET_KEY, algorithm=TokenManager.ALGORITHM
        )

    @staticmethod
    def validate_token(token: str) -> dict:
        """
        Проверяет токен на валидность.
        """
        try:
            payload = jwt.decode(
                token, TokenManager.SECRET_KEY, algorithms=[TokenManager.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def role_required(required_role: str):
        """
        Проверяет роль пользователя, обращаясь к backend для извлечения данных.
        """

        async def dependency(token: Optional[str] = Header(None)):
            if not token:
                raise HTTPException(status_code=401, detail="Access token is missing")

            try:
                payload = TokenManager.validate_token(token)
                user_email = payload.get("email")
                user_password = payload.get("password")
                user_phone = payload.get("phone")

                if not user_email or not user_password or not user_phone:
                    raise HTTPException(status_code=401, detail="Invalid token payload")

                user_data_response = await messagePublisher.process_request(
                    "get_user",
                    "user_updates",
                    "user_updates_response",
                    {
                        "password": user_password,
                        "email": user_email,
                        "phone": user_phone,
                    },
                )

                if not user_data_response or "data" not in user_data_response:
                    raise HTTPException(status_code=404, detail="User not found")

                user_data = json.loads(user_data_response["data"])

                if not user_data:
                    raise HTTPException(status_code=404, detail="User not found")

                user_role = user_data.get("role")
                if not user_role or user_role != required_role:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Action requires '{required_role}' role",
                    )

            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token has expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")

        return dependency

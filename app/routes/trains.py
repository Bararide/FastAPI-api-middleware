from app.routes import seats

from fastapi import APIRouter, Depends
from app.RabbitMQ.MessagePublisher import MessagePublisher
from app.tokens.TokenManager import TokenManager

router = APIRouter()

message_publisher = MessagePublisher()

router.include_router(seats.router, prefix="/seats", tags=["Seats"])


@router.get("/")
async def get_trains():
    return await message_publisher.process_request(
        "get_trains", "train_updates", "train_updates_response"
    )


@router.get("/id/{id}")
async def get_train(id: int):
    return await message_publisher.process_request(
        "get_train_by_id", "train_updates", "train_updates_response", {"id": id}
    )


@router.get("/name/{name}")
async def get_train_by_name(name):
    return await message_publisher.process_request(
        "get_train_by_name", "train_updates", "train_updates_response", {"name": name}
    )


@router.post("/")
async def add_train(
    name: str,
    train_type: str,
    manufacturing_date: str,
    operation_status: str,
    company: str,
    token: str = Depends(TokenManager.role_required("admin")),
):
    return await message_publisher.process_request(
        "add_train",
        "train_updates",
        "train_updates_response",
        {
            "name": name,
            "train_type": train_type,
            "manufacturing_date": manufacturing_date,
            "operation_status": operation_status,
            "company": company,
        },
    )


@router.delete("/id/{id}")
async def remove_train_by_id(
    id: int, token: str = Depends(TokenManager.role_required("admin"))
):
    return await message_publisher.process_request(
        "delete_train_by_id", "train_updates", "train_updates_response", {"id": id}
    )


@router.delete("/name/{name}")
async def remove_train_by_name(
    name: str, token: str = Depends(TokenManager.role_required("admin"))
):
    return await message_publisher.process_request(
        "delete_train_by_name",
        "train_updates",
        "train_updates_response",
        {"name": name},
    )

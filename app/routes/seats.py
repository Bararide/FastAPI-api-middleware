from fastapi import APIRouter, Depends
from app.RabbitMQ.MessagePublisher import MessagePublisher
from app.tokens.TokenManager import TokenManager

router = APIRouter()

message_publisher = MessagePublisher()


@router.get("/train_car")
async def get_train_cars(car_type: str):
    return await message_publisher.process_request(
        "get_trains_with_car_type",
        "train_updates",
        "train_updates_response",
        {"car_type": car_type},
    )


@router.get("/train_name")
async def get_seats_by_train_name(train_name: str):
    return await message_publisher.process_request(
        "get_seats_by_train_name",
        "train_updates",
        "train_updates_response",
        {"train_name": train_name},
    )


@router.get("/train_by_route")
async def get_seats_on_train_by_route(route_name: str):
    return await message_publisher.process_request(
        "get_seats_by_route_name",
        "train_updates",
        "train_updates_response",
        {"route_name": route_name},
    )


@router.get("/train_by_route_and_train_type")
async def get_seats_on_train_by_route(route_name: str, train_type: str):
    return await message_publisher.process_request(
        "get_seats_by_route_name",
        "train_updates",
        "train_updates_response",
        {"route_name": route_name, "train_type": train_type},
    )

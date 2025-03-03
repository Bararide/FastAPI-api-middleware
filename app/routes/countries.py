from fastapi import APIRouter
from app.RabbitMQ.MessagePublisher import MessagePublisher

router = APIRouter()

message_publisher = MessagePublisher()


@router.get("/")
async def get_countries():
    return await message_publisher.process_request(
        "get_countries", "country_updates", "country_updates_response"
    )


@router.get("/id/{id}")
async def get_country_by_id(id: int):
    return await message_publisher.process_request(
        "get_country_by_id", "country_updates", "country_updates_response", {"id": id}
    )


@router.get("/name/{name}")
async def get_country_by_name(name: str):
    return await message_publisher.process_request(
        "get_country_by_name",
        "country_updates",
        "country_updates_response",
        {"name": name},
    )


@router.post("/")
async def add_country(name: str):
    return await message_publisher.process_request(
        "add_country", "country_updates", "country_updates_response", {"name": name}
    )


@router.put("/{id}")
async def update_country(id: int, name: str):
    return await message_publisher.process_request(
        "update_country",
        "country_updates",
        "country_updates_response",
        {"id": id, "name": name},
    )


@router.delete("/id/{id}")
async def delete_country(id: int):
    return await message_publisher.process_request(
        "delete_country_by_id",
        "country_updates",
        "country_updates_response",
        {"id": id},
    )


@router.delete("/name/{name}")
async def delete_country_by_name(name: str):
    return await message_publisher.process_request(
        "delete_country_by_name",
        "country_updates",
        "country_updates_response",
        {"name": name},
    )

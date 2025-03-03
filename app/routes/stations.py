import pika
import logging
from fastapi import APIRouter, HTTPException
from app.RabbitMQ.MessagePublisher import MessagePublisher
import json

router = APIRouter()

message_publisher = MessagePublisher()


@router.get("/")
async def get_stations():
    return await message_publisher.process_request(
        "get_stations", "station_updates", "station_updates_response"
    )


@router.get("/id/{id}")
async def get_station_by_id(id: int):
    return await message_publisher.process_request(
        "get_station_by_id", "station_updates", "station_updates_response", {"id": id}
    )


@router.get("/name/{name}")
async def get_station_by_name(name: str):
    return await message_publisher.process_request(
        "get_station_by_name",
        "station_updates",
        "station_updates_response",
        {"name": name},
    )


@router.post("/")
async def add_station(name: str, lon: float, lat: float, zone_id: int, city_id: int):
    payload = {
        "name": name,
        "lon": lon,
        "lat": lat,
        "zone_id": zone_id,
        "city_id": city_id,
    }
    return await message_publisher.process_request(
        "add_station", "station_updates", "station_updates_response", payload
    )


@router.delete("/id/{id}")
async def delete_station_by_id(id: int):
    return await message_publisher.process_request(
        "delete_station_by_id",
        "station_updates",
        "station_updates_response",
        {"id": id},
    )


@router.delete("/name/{name}")
async def delete_station_by_name(name: str):
    return await message_publisher.process_request(
        "delete_station_by_name",
        "station_updates",
        "station_updates_response",
        {"name": name},
    )

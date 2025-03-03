from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import trains, users, countries, stations
from app.db.mongodb import init_mongodb

app = FastAPI(title="FastAPI Middleware", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_mongodb()


@app.on_event("shutdown")
async def shutdown():
    await init_mongodb(close=True)


# Роуты
app.include_router(trains.router, prefix="/trains", tags=["Trains"])
app.include_router(countries.router, prefix="/countries", tags=["Countries"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(stations.router, prefix="/stations", tags=["Stations"])

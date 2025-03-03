from motor.motor_asyncio import AsyncIOMotorClient

mongodb_client = None

async def init_mongodb(close=False):
    global mongodb_client
    if close and mongodb_client:
        mongodb_client.close()
    elif not close:
        mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
        print("MongoDB connected successfully.")

from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app

DATABASENAME = "EDCDB"

app.config['MONGO_URI'] = "mongodb://localhost:27017"

client = AsyncIOMotorClient(app)


def get_database():
    return client[DATABASENAME]


if __name__ == "__main__":
    dbname = get_database()

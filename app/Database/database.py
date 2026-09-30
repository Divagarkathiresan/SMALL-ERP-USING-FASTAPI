import os
import logging
import redis.asyncio as redis

from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True 
)

try:
    # Create MongoDB client
    client = MongoClient(
        os.getenv("MONGO_URI"),
        serverSelectionTimeoutMS=5000  # Wait at most 5 seconds
    )

    # Force the connection
    client.admin.command("ping")

    # Select database
    db = client[os.getenv("DB_NAME")]

    # Collections
    product_collection = db["products"]
    user_collection = db["users"]
    inventory_collection=db["inventory"]
    orders_collection=db["orders"]
    orderList_collection=db["orderList"]
    invoice_collection=db["invoice"]
    logger.info("MongoDB connected successfully.")

except Exception:
    logger.exception("MongoDB connection failed.")
    raise
import os
from dotenv import load_dotenv
from redis_om import get_redis_connection

load_dotenv()

# Redis connection
redis = get_redis_connection(
    url=os.getenv("REDIS_HOST"),
    decode_responses=True
)

# Validate connection
if redis.ping():
    print("Redis connected successfully")

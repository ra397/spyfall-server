from redis_om import HashModel
from config.redis import redis

class BaseModel(HashModel):
    class Meta:
        database = redis
        global_key_prefix = "spyfall"
from redis_om import Field, HashModel
from .redis import redis

class Player(HashModel):
    player_name: str = Field(min_length=2, max_length=12)
    socket_id: str = Field(index=True)
    game_id: str = Field(index=True)  # References Game.pk
    current_occupation: str

    class Meta:
        database = redis
        global_key_prefix = "spyfall"
        model_key_prefix = "player"
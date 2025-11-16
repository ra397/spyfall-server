from redis_om import Field, HashModel
from .BaseModel import BaseModel

class Player(BaseModel):
    player_name: str = Field(min_length=2, max_length=12)
    socket_id: str = Field(index=True)
    uid : str = Field(index=True)
    game_id: str = Field(index=True)  # References Game.pk
    current_occupation: str

    class Meta:
        model_key_prefix = "player"
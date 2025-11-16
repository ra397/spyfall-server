import datetime
import random
import string
from redis_om import Field, HashModel
from typing import Literal
from datetime import datetime, timezone
from models.BaseModel import BaseModel

class Game(BaseModel):
    game_code: str = Field(index=True)
    current_round_duration: int = Field(ge=360, le=720)
    status: Literal['game', 'lobby'] = Field(default='lobby')
    current_location: str
    game_owner: str = Field(index=True)  # References Player.pk
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    @staticmethod
    def generate_game_code() -> str:
        return ''.join(random.choices(string.ascii_uppercase, k=5))

    class Meta:
        model_key_prefix = "game"
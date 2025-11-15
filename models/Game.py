import datetime
from redis_om import Field, HashModel
from typing import Literal
from datetime import datetime, timezone
from BaseModel import BaseModel

class Game(BaseModel):
    game_code: str = Field(index=True)
    current_round_duration: int = Field(ge=360, le=720)
    status: Literal['game', 'lobby'] = Field(default='lobby')
    current_location: str
    game_owner: str = Field(index=True)  # References Player.pk
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    class Meta:
        model_key_prefix = "game"
from pydantic import BaseModel


class Level(BaseModel):
    level_id: str
    league_number: int
    level_type_id: str
    game_type_id: str
    event_id: str
    heat_number: int
    course: str
    run_time_seconds: float
    total_feet: float
    is_qualified: bool


class LevelType(BaseModel):
    level_type_id: str
    level_type_name: str

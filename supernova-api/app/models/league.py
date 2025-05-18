from pydantic import BaseModel


class LevelModel(BaseModel):
    level_id: str | None
    league_number: int | None
    level_type_id: str | None
    game_type_id: str | None
    event_id: str | None
    heat_number: int | None
    course: str | None
    run_time_seconds: float | None
    total_feet: float | None
    is_qualified: bool | None


class LevelTypeModel(BaseModel):
    level_type_id: str | None
    level_type_name: str | None


class GameTypeModel(BaseModel):
    game_type_id: str | None
    is_game_type_active: bool | None


class EventModel(BaseModel):
    event_id: str | None
    event_start_timestamp: str | None
    event_end_timestamp: str | None
    event_name: str | None

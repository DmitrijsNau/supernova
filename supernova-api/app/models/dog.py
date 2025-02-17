from pydantic import BaseModel


class DogModel(BaseModel):
    league_number: int
    dog_name: str
    main_handler_id: str
    alternate_handler_id: str
    call_name: str
    breed: str
    height: float
    jump_height: int
    current_level_type_id: str
    is_reactive: bool
    people: bool
    dogs: bool
    is_virtual: bool


class HandlerModel(BaseModel):
    handler_id: str
    league_number: int
    handler_name: str
    handler_email: str

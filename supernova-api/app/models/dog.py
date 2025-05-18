from pydantic import BaseModel


class DogModel(BaseModel):
    league_number: int | None
    dog_name: str | None
    main_handler_id: str | None
    alternate_handler_id: str | None
    call_name: str | None
    breed: str | None
    height: float | None
    jump_height: int | None
    current_level_type_id: str | None
    is_reactive: bool | None
    people: bool | None
    dogs: bool | None
    is_virtual: bool | None
    is_dog_active: bool | None

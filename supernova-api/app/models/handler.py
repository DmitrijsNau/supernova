from pydantic import BaseModel


class HandlerModel(BaseModel):
    handler_id: str | None
    league_number: int | None
    handler_name: str | None
    handler_email: str | None
    handler_role: str | None

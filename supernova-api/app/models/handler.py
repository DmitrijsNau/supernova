from pydantic import BaseModel


class HandlerModel(BaseModel):
    handler_id: str
    league_number: int
    handler_name: str
    handler_email: str
    handler_role: str

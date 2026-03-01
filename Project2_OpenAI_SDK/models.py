from pydantic import BaseModel


class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str
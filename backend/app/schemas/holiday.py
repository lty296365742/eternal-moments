from pydantic import BaseModel


class ToggleRemindRequest(BaseModel):
    remind_enabled: bool

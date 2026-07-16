from datetime import time
from pydantic import BaseModel, ConfigDict


class RoomResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class TimeSlotResponse(BaseModel):
    id: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)
    
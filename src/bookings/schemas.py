import datetime
from datetime import time
from pydantic import BaseModel, ConfigDict, field_validator, model_validator



class BookingCreate(BaseModel):
    room_id: int
    time_slot_id: int
    date: datetime.date

    model_config = ConfigDict(from_attributes=True)

    @field_validator("date")
    @classmethod
    def date_must_not_be_in_past(cls, v: datetime.date) -> datetime.date:
        if v < datetime.date.today():
            raise ValueError("Booking date cannot be in the past.")
        return v
     
class BookingResponse(BaseModel):
    id: int
    room_name: str
    booking_date: datetime.date
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def flatten_orm_relations(cls, data):
        # Checks if incoming data is an ORM instance instead of a dict
        if not isinstance(data, dict):
            return {
                "id": data.id,
                "room_name": data.room.name,
                "booking_date": data.date,
                "start_time": data.time_slot.start_time,
                "end_time": data.time_slot.end_time,
            }
        return data

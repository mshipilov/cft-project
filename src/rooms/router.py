from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, status, Depends, Query

from .service import read_rooms, read_available_slots
from .schemas import RoomResponse, TimeSlotResponse
from ..database import SessionDep
from ..dependencies import UserDep


router = APIRouter(
    prefix='/rooms',
    tags=["Комнаты"]
    )

@router.get("")
async def get_rooms(
    current_user: UserDep,
    db: SessionDep
    ) -> list[RoomResponse]:
    rooms = await read_rooms(db=db)
    return rooms

@router.get("/{room_id}/available-slots")
async def get_available_slots(
    current_user: UserDep,
    room_id: int,
    db: SessionDep,
    booking_date: date = Query(
        alias="date", 
        description="The target booking date in YYYY-MM-DD format"
        )
    ) -> list[TimeSlotResponse]:
    """Returns available slots for a room on a query-specified date."""
    slots = await read_available_slots(db=db, room_id=room_id, booking_date=booking_date)
    return slots


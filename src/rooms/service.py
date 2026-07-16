from datetime import date, time

from fastapi import HTTPException, status
from sqlalchemy import select, insert, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Room, TimeSlot, Booking
from .schemas import TimeSlotResponse, RoomResponse


async def read_rooms(db: AsyncSession) -> list[RoomResponse]:
    statement = select(Room)
    result = await db.execute(statement)
    rooms = result.scalars().all()
    return [RoomResponse.model_validate(room) for room in rooms]  # show type checker we can translate Room -> RoomResponse


async def read_available_slots(room_id: int, booking_date: date | None, db: AsyncSession) -> list[TimeSlotResponse]:
    today = date.today()

    if booking_date is None:
        booking_date = today

    if booking_date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot read time slots for past dates."
        )
    
    room_ids = [room.id for room in await read_rooms(db=db)]
    if room_id not in room_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requsested room id doesn't exist"
        )
    
    booked_slots_subquery = (
        select(Booking.time_slot_id)
        .where(Booking.room_id == room_id, Booking.date == booking_date)
        .scalar_subquery()
    )

    statement = (
        select(TimeSlot)
        .where(TimeSlot.id.not_in(booked_slots_subquery))
        .order_by(TimeSlot.start_time)
    )

    result = await db.execute(statement)
    time_slots = result.scalars().all()
    
    return [TimeSlotResponse.model_validate(slot) for slot in time_slots] # show type checker we can translate TimeSlot -> TimeSlotResponse


async def populate_db_time_slots(db: AsyncSession):
    stmt = select(func.count()).select_from(TimeSlot)
    number_of_slots_in_db = await db.scalar(stmt)
    if number_of_slots_in_db == 0:

        slots_data = [
            TimeSlot(start_time=time(9, 0), end_time=time(11, 0)),
            TimeSlot(start_time=time(11, 0), end_time=time(13, 0)),
            TimeSlot(start_time=time(13, 0), end_time=time(16, 0)),
            TimeSlot(start_time=time(16, 0), end_time=time(18, 0)),
        ]
        db.add_all(slots_data)
        await db.commit()

async def populate_db_rooms(db: AsyncSession):
    stmt = select(func.count()).select_from(Room)
    number_of_rooms = await db.scalar(stmt)
    if number_of_rooms == 0:

        rooms_data = [
            Room(name='Конференц зал'),
            Room(name='Переговорная комната'),
            Room(name='Комната отдыха'),
        ]
        db.add_all(rooms_data)
        await db.commit()
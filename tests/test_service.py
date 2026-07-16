import datetime
import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.users.service import read_users
from src.rooms.service import read_rooms, read_available_slots
from src.rooms.schemas import RoomResponse, TimeSlotResponse
from src.rooms.service import populate_db_time_slots, populate_db_rooms
from src.users.service import populate_db_users
from src.bookings.service import create_booking, read_bookings, delete_booking
from src.bookings.schemas import BookingCreate, BookingResponse

# use production database for simplicity
@pytest_asyncio.fixture(scope="session")
async def db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback() 
            await session.close()   

@pytest.mark.asyncio(scope="session")
async def test_read_rooms(db: AsyncSession):
    rooms = await read_rooms(db=db)
    assert isinstance(rooms[0], RoomResponse)
    await db.rollback()

@pytest.mark.asyncio(scope="session")
async def test_read_available_slots(db: AsyncSession):
    rooms = await read_rooms(db=db)
    room = rooms[0]
    slots = await read_available_slots(room_id=room.id, booking_date=datetime.date.today(), db=db)
    assert isinstance(slots[0], TimeSlotResponse)
    await db.rollback()

@pytest.mark.asyncio(scope="session")
async def test_create_booking(db: AsyncSession):
    users = await read_users(db=db)
    user = users[0]

    rooms = await read_rooms(db=db)
    room = rooms[0]

    time_slots = await read_available_slots(room_id=room.id, booking_date=datetime.date.today(), db=db)
    time_slot = time_slots[0]

    booking_create = BookingCreate(room_id=room.id, time_slot_id=time_slot.id, date=datetime.date.today())
    booking = await create_booking(user_input=booking_create, current_user=user, db=db)

    assert isinstance(booking, BookingResponse)
    await db.rollback()

@pytest.mark.asyncio(scope="session")
async def test_read_bookings(db: AsyncSession):
    users = await read_users(db=db)
    user = users[0]

    bookings = await read_bookings(current_user=user, db=db)
    booking = bookings[0]

    assert isinstance(booking, BookingResponse)
    await db.rollback()

@pytest.mark.asyncio(scope="session")
async def test_delete_booking(db: AsyncSession):
    users = await read_users(db=db)
    user = users[0]

    bookings = await read_bookings(current_user=user, db=db)
    booking = bookings[0]

    await delete_booking(booking_id=booking.id, current_user=user, db=db)

    await db.rollback()
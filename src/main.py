from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI

from . import log_config
from .database import create_db_tables, AsyncSessionLocal
from .auth.router import router as auth_router
from .bookings.router import router as booking_router
from .rooms.router import router as room_router
from .rooms.service import populate_db_time_slots, populate_db_rooms
from .users.service import populate_db_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_tables()
    async with AsyncSessionLocal() as db:
        create_users = asyncio.create_task(populate_db_users(db=db))
        create_slots = asyncio.create_task(populate_db_time_slots(db=db))
        create_rooms = asyncio.create_task(populate_db_rooms(db=db))
        await create_users
        await create_slots
        await create_rooms
    yield


app = FastAPI(
    title="Сервис бронирования комнат",
    lifespan=lifespan
    )

app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(room_router)
print('app started')

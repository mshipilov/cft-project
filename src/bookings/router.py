from fastapi import APIRouter, Depends, status, HTTPException
from ..database import SessionDep
from ..dependencies import UserDep

from .schemas import BookingCreate, BookingResponse
from .service import create_booking, delete_booking, read_bookings

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"]
    )

@router.post("", status_code=status.HTTP_201_CREATED)
async def make_booking(
    user_input: BookingCreate,
    db: SessionDep,
    current_user: UserDep
    ) -> BookingResponse:
    new_booking = await create_booking(user_input=user_input, current_user=current_user, db=db)
    return new_booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    db: SessionDep,
    current_user: UserDep
    ):
    await delete_booking(booking_id=booking_id, current_user=current_user, db=db)

@router.get("")
async def get_bookings(
    db: SessionDep,
    current_user: UserDep
    )  -> list[BookingResponse]:
    """Get personal bookings for user. Get all bookings for admin """
    result = await read_bookings(current_user=current_user, db=db)
    return result
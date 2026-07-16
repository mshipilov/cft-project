from datetime import date
from typing import Optional
import logging

from fastapi import HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Booking, User
from .schemas import BookingCreate, BookingResponse


logger = logging.getLogger(f'app.{__name__}')

async def create_booking(
        user_input: BookingCreate, 
        current_user: User, 
        db: AsyncSession
        ) -> BookingResponse:
    
    logger.info(f'creating new booking {user_input} by {current_user}')

    today = date.today()
    
    if user_input.date < today:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot book a time slot for a past date (today: {today})."
        )
    
    new_booking = Booking(
        **user_input.model_dump(),
        user_id = current_user.id
    )
 
    db.add(new_booking)

    try:
        await db.flush()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested booking details not found"
        )
    
    full_new_booking = await read_booking(booking_id=new_booking.id, db=db)  # booking with relationships (room.name, ...)

    try:
        await db.commit()  # commit here (not in db session manager) to avoid race condition
        
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot has already been reserved by another user."
        )

    return BookingResponse.model_validate(full_new_booking)

async def read_booking(booking_id: int, db: AsyncSession) -> Optional[BookingResponse]:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.room),
            selectinload(Booking.time_slot)
        )
    )
    result = await db.execute(stmt)
    booking = result.scalars().first()
    return BookingResponse.model_validate(booking)

async def read_bookings(current_user: User, db: AsyncSession) -> list[BookingResponse]:
    stmt = (
        select(Booking)
        .options(
            selectinload(Booking.room),
            selectinload(Booking.time_slot)
        )
    )
    # filter personal bookings for non-admin
    if current_user.role.name != 'admin':
        stmt = stmt.where(Booking.user_id == current_user.id)
    
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    return [BookingResponse.model_validate(booking) for booking in bookings]

async def delete_booking(booking_id: int, current_user: User, db: AsyncSession) -> None:
    logger.info(f'deleting booking with id {booking_id} by {current_user}')

    # get booking
    stmt = select(Booking).where(Booking.id == booking_id)
    result = await db.execute(stmt)
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # forbid to delete someone else's booking by non-admin
    if current_user.role.name != 'admin' and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden deletion of someone else's booking by non-admin "
            )
  
    # delete booking
    stmt = delete(Booking).where(Booking.id == booking_id)
    await db.execute(stmt)
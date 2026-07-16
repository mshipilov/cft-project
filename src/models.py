import datetime

from sqlalchemy import ForeignKey, String, Boolean, Date, Time, Table, Column, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(unique=True, index=True)  # index for authentication
    hashed_password: Mapped[str] = mapped_column(String(128))
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"))
    
    role: Mapped["Role"] = relationship(back_populates="users")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

    def __repr__(self):
        return f'User with email {self.email}'
    

class Role(Base):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    
    users: Mapped[list["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f'Role {self.name}'
    

class Room(Base):
    __tablename__ = "room"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)

    bookings: Mapped[list["Booking"]] = relationship(back_populates='room')

    def __repr__(self):
        return f'Room {self.name}'
    

class TimeSlot(Base):
    __tablename__ = "time_slot"

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_start_end_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    end_time: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="time_slot")

    def __repr__(self):
        return f'Time slot from {self.start_time} to {self.end_time}'

    
class Booking(Base):
    __tablename__ = "booking"

    __table_args__ = (
        UniqueConstraint("room_id", "date", "time_slot_id", name="uq_room_date_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, index=True)  # index for search by date
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"))
    time_slot_id: Mapped[int] = mapped_column(ForeignKey("time_slot.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)  # index for search by user

    room: Mapped["Room"] = relationship(back_populates='bookings')
    time_slot: Mapped["TimeSlot"] = relationship(back_populates='bookings')
    user: Mapped["User"] = relationship(back_populates='bookings')

    def __repr__(self):
        return f'Booking for room_id {self.room_id} on {self.time_slot} {self.date}'
    

from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils import encrypt_pass
from ..models import User, Role


async def read_roles(db: AsyncSession) -> list[Role]:
    statement = select(Role)
    result = await db.execute(statement)
    roles = result.scalars().all()
    return list(roles)


async def read_users(db: AsyncSession) -> list[User]:
    # selectinload - to load user.role relationship
    statement = select(User).options(selectinload(User.role))
    result = await db.execute(statement)
    users = result.scalars().all()
    return list(users)


async def read_user(*, user_id: int | str | None =None, email:str | None =None, db: AsyncSession) -> Optional[User]:
    # selectinload - to load user.role relationship
    stmt = select(User).options(selectinload(User.role))
    
    if user_id:
        user_id = int(user_id)
        stmt = stmt.where(User.id == user_id)
    elif email:
        stmt = stmt.where(User.email == email)
    else:
        return None
    
    result = await db.execute(stmt)
    user = result.scalars().first()
    return user


async def populate_db_users(db: AsyncSession):
    if not await read_roles(db=db):
        admin_role = Role(name='admin')
        user_role = Role(name='user')
    
        admin_user = User(name='Админ Пользователь',
                          email='admin@admin.com',
                          hashed_password=encrypt_pass('123'),
                          role=admin_role
                          )
        regular_user = User(name='Обычный Пользователь',
                            email='user@user.com',
                            hashed_password=encrypt_pass('123'),
                            role=user_role
                            )
        
        db.add_all([admin_user, regular_user])
        await db.commit()
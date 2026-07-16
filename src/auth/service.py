import logging

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .utils import encode_token
from ..users.service import read_user
from ..utils import check_encrypred_pass

logger = logging.getLogger(f'app.{__name__}')


async def auth_user(user_input: OAuth2PasswordRequestForm, db: AsyncSession) -> str:
    email = user_input.username
    password = user_input.password
    logger.debug(f'authentication for email {email}')
    user = await read_user(email=email, db=db)

    if not user or not check_encrypred_pass(password=password, hashed_pass=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong user email or password"
        )

    token = encode_token(user_id=user.id)
    return token

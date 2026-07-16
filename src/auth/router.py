from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..database import SessionDep
from .service import auth_user
from .schemas import TokenResponse


router = APIRouter(prefix='/auth',
                   tags=["Аутентификация"]
                   )

@router.post("")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep
    ) -> TokenResponse:
    token = await auth_user(user_input=form_data, db=db)
    return TokenResponse(access_token=token)

from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, Request
from fastapi import HTTPException, status
import jwt

from .models import Base, User, Role, Booking
from .database import SessionDep
from .auth.utils import decode_token
from .users.service import read_user



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(
    token: TokenDep,
    db: SessionDep
) -> User:
    """Validates the JWT token and returns the authenticated user."""
    print('token', token)
    try:
        payload = decode_token(token)
        print('payload', payload)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.PyJWTError:  # Handles expired or malformed tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await read_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


UserDep = Annotated[User, Depends(get_current_user)]


'''
async def get_admin_user(
        current_user: UserDep,
        db: SessionDep
        ) -> User:
    is_admin = current_user.role == 'admin'

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    return current_user
    

AdminUserDep = Annotated[User, Depends(get_admin_user)]
'''

'''
class RoleChecker:
    
    def __init__(
            self, 
            resource: Optional[type[Base]] = None,
            ):
        
        self.resource = resource
        self.access_denied_exception =HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied"
        )

    async def __call__(
            self, 
            request: Request,
            current_user: Annotated[User, Depends(get_current_user)],
            ):
        
        # admin has FULL access
        if current_user.role.name == 'admin':
            return current_user
        
        # user has access only to Bookings
        if current_user.role.name == 'user' and self.resource == Booking:
            await self.check_booking_individual_permission(request=request, current_user=current_user)
    
    
    async def check_booking_individual_permission(
            self,
            request: Request, 
            current_user: User
    ):
        booking_id = request.path_params.get('id')
        if not booking_id:
            raise HTTPException(status_code=400, detail=f"booking_id not provided in request")
        
        booking = await read_booking(booking_id=booking_id, db=db)
        if not booking:
            raise HTTPException(status_code=400, detail=f"booking not found")

        owner_id = booking.user_id
    
        if current_user.id == owner_id:
            return current_user
        else:
            raise HTTPException(status_code=403, detail=f"current_user does not own requested booking")'''

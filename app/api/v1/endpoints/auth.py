from fastapi import APIRouter, HTTPException, Request, status
from app.models.auth import Token, UserCreate, SigninRequest, TokenRefresh, TokenVerifyRequest, SignoutRequest
from app.domain.services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth")

@auth_router.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    try:
        token = await AuthService.signup(user)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@auth_router.post("/signin", response_model=Token)
async def signin(payload: SigninRequest):
    try:
        token = await AuthService.signin(payload)
        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@auth_router.post("/signout")
async def signout(signout_request: SignoutRequest, request: Request):
    user = request.state.user
    refresh_token = signout_request.refresh_token
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token not found")
    success = await AuthService.signout(user_id=user.id, refresh_token=refresh_token)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to log out")

    return {"msg": "Successfully logged out"}

@auth_router.post("/token/verify")
async def verify_token(payload: TokenVerifyRequest):
    is_valid = await AuthService.verify_token(payload.token)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"valid": True}

@auth_router.post("/token/refresh", response_model=Token)
async def refresh_token(token_refresh: TokenRefresh):
    try:
        new_token = await AuthService.refresh_token(token_refresh)
        return new_token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.token_repository import RefreshTokenRepository
from app.models.auth import UserCreate, UserInfo, Token, SigninRequest, TokenRefresh
from app.core.security import create_access_token, create_refresh_token, save_refresh_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

class AuthService:
    @staticmethod
    async def signup(user: UserCreate) -> Token:
        existing_user_by_wallet = await UserRepository.get_by_wallet_address(user.wallet_address)
        if existing_user_by_wallet:
            raise ValueError("User with this wallet address already exists")

        existing_user_by_display_name = await UserRepository.get_by_display_name(user.display_name)
        if existing_user_by_display_name:
            raise ValueError("Display name already taken")

        db_user = await UserRepository.create({
            "wallet_address": user.wallet_address,
            "display_name": user.display_name,
            "bio": user.bio,
            "profile_photo_url": user.profile_photo_url,
            "created_at": datetime.now(timezone.utc),
        })

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_signup = create_refresh_token(
            data={"sub": db_user.wallet_address}, expires_delta=refresh_token_expires
        )

        save_refresh_token(
            user_id=db_user.id,
            token=refresh_token_signup,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires
        )

        user_info = UserInfo(
            id=db_user.id,
            wallet_address=db_user.wallet_address,
            display_name=db_user.display_name,
            bio=db_user.bio,
            profile_photo_url=db_user.profile_photo_url,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            roles=db_user.roles,
            invited_by=db_user.invited_by,
            rank=db_user.rank,
            followers_count=db_user.followers_count
        ).model_dump()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_signup,
            token_type="bearer",
            user_info=user_info
        )

    @staticmethod
    async def signin(payload: SigninRequest) -> Token:
        db_user = await UserRepository.get_by_wallet_address(payload.wallet_address)
        if not db_user:
            raise ValueError("User not found")
        
        await UserRepository.update_last_login(db_user)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_signin = create_refresh_token(
            data={"sub": db_user.wallet_address}, expires_delta=refresh_token_expires
        )
        
        save_refresh_token(
            user_id=db_user.id,
            token=refresh_token_signin,
            expires_at=datetime.now(timezone.utc) + refresh_token_expires
        )
        
        user_info = UserInfo(
            id=db_user.id,
            wallet_address=db_user.wallet_address,
            display_name=db_user.display_name,
            bio=db_user.bio,
            profile_photo_url=db_user.profile_photo_url,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            roles=db_user.roles,
            invited_by=db_user.invited_by,
            rank=db_user.rank,
            followers_count=db_user.followers_count
        ).model_dump()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token_signin,
            token_type="bearer",
            user_info=user_info
        )
        
    @staticmethod
    async def signout(user_id: UUID, refresh_token: str) -> bool:
        return await RefreshTokenRepository.delete_by_user_and_token(user_id, refresh_token)

    @staticmethod
    async def verify_token(token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            wallet_address: str = payload.get("sub")
            if wallet_address is None:
                return False

            # Fetch user and verify token data against database records
            user = await UserRepository.get_by_wallet_address(wallet_address)
            if not user or \
               payload.get("username") != user.display_name or \
               payload.get("avatar") != user.profile_photo_url or \
               payload.get("wallet_address") != user.wallet_address:
                return False
            return True
        except JWTError:
            return False

    @staticmethod
    async def refresh_token(token_refresh: TokenRefresh) -> Token:
        try:
            print(token_refresh)
            payload = jwt.decode(token_refresh.refresh_token, SECRET_KEY, algorithms=ALGORITHM)
            wallet_address: str = payload.get("sub")
            print(wallet_address)
            if wallet_address is None:
                raise ValueError("Invalid refresh token payload")

            user = await UserRepository.get_by_wallet_address(wallet_address)
            if not user:
                raise ValueError("User not found")
            stored_refresh_token = await RefreshTokenRepository.get_by_user_and_token(user.id, token_refresh.refresh_token)
            print(stored_refresh_token)
            if not stored_refresh_token:
                raise ValueError("Stored refresh token not found")
            expires_at = stored_refresh_token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
                
            if expires_at < datetime.now(timezone.utc):
                raise ValueError("Expired refresh token")
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_access_token(
                data={"sub": user.wallet_address}, expires_delta=access_token_expires
            )
            new_refresh_token = create_refresh_token(
                data={"sub": user.wallet_address}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            await RefreshTokenRepository.delete(stored_refresh_token)
            await RefreshTokenRepository.save(
                user_id=user.id,
                token=new_refresh_token,
                expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            )

            user_info = UserInfo(
                id=user.id,
                wallet_address=user.wallet_address,
                display_name=user.display_name,
                bio=user.bio,
                profile_photo_url=user.profile_photo_url,
                created_at=user.created_at,
                last_login=user.last_login,
                roles=user.roles,
                invited_by=user.invited_by,
                rank=user.rank,
                followers_count=user.followers_count
            ).model_dump()

            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                user_info=user_info
            )

        except JWTError:
            raise ValueError("Invalid refresh token")
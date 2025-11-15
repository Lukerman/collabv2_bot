from db.mongo import get_database
from bot.models.models import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def get_or_create_user(user_id: int, username: Optional[str] = None,
                                  first_name: Optional[str] = None,
                                  last_name: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        db = get_database()
        
        user_data = await db.users.find_one({"user_id": user_id})
        
        if user_data:
            return User(**user_data)
        
        # Create new user
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        await db.users.insert_one(user.model_dump())
        logger.info(f"Created new user: {user_id}")
        
        return user

    @staticmethod
    async def update_current_room(user_id: int, room_code: Optional[str]):
        """Update user's current room"""
        db = get_database()
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"current_room_code": room_code}}
        )

    @staticmethod
    async def get_user(user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = get_database()
        user_data = await db.users.find_one({"user_id": user_id})
        return User(**user_data) if user_data else None

    @staticmethod
    async def is_admin(user_id: int) -> bool:
        """Check if user is admin"""
        user = await UserService.get_user(user_id)
        return user.role == "admin" if user else False

    @staticmethod
    async def get_all_users(skip: int = 0, limit: int = 50):
        """Get all users with pagination"""
        db = get_database()
        cursor = db.users.find().skip(skip).limit(limit).sort("created_at", -1)
        users = await cursor.to_list(length=limit)
        return [User(**u) for u in users]

    @staticmethod
    async def count_users() -> int:
        """Count total users"""
        db = get_database()
        return await db.users.count_documents({})

    @staticmethod
    async def update_user_role(user_id: int, role: str):
        """Update user role"""
        db = get_database()
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"role": role}}
        )
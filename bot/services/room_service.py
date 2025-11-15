from db.mongo import get_database
from bot.models.models import Room
from typing import Optional, List
import string
import random
import logging

logger = logging.getLogger(__name__)


class RoomService:
    @staticmethod
    def generate_room_code(length: int = 8) -> str:
        """Generate unique room code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    async def create_room(name: str, owner_id: int, description: Optional[str] = None) -> Room:
        """Create a new study room"""
        db = get_database()
        
        # Generate unique code
        while True:
            code = RoomService.generate_room_code()
            existing = await db.rooms.find_one({"code": code})
            if not existing:
                break
        
        room = Room(
            code=code,
            name=name,
            description=description,
            owner_id=owner_id,
            members=[owner_id]
        )
        
        await db.rooms.insert_one(room.model_dump())
        logger.info(f"Created room {code} by user {owner_id}")
        
        return room

    @staticmethod
    async def get_room(code: str) -> Optional[Room]:
        """Get room by code"""
        db = get_database()
        room_data = await db.rooms.find_one({"code": code, "is_active": True})
        return Room(**room_data) if room_data else None

    @staticmethod
    async def get_room_by_chat_id(chat_id: int) -> Optional[Room]:
        """Get room by linked Telegram chat ID"""
        db = get_database()
        room_data = await db.rooms.find_one({"linked_chat_id": chat_id, "is_active": True})
        return Room(**room_data) if room_data else None

    @staticmethod
    async def join_room(code: str, user_id: int) -> bool:
        """Add user to room"""
        db = get_database()
        result = await db.rooms.update_one(
            {"code": code, "is_active": True},
            {"$addToSet": {"members": user_id}}
        )
        return result.modified_count > 0 or result.matched_count > 0

    @staticmethod
    async def leave_room(code: str, user_id: int) -> bool:
        """Remove user from room"""
        db = get_database()
        result = await db.rooms.update_one(
            {"code": code},
            {"$pull": {"members": user_id}}
        )
        return result.modified_count > 0

    @staticmethod
    async def link_chat(code: str, chat_id: int, user_id: int) -> bool:
        """Link Telegram group to room (only owner can do this)"""
        db = get_database()
        room = await RoomService.get_room(code)
        
        if not room or room.owner_id != user_id:
            return False
        
        result = await db.rooms.update_one(
            {"code": code},
            {"$set": {"linked_chat_id": chat_id}}
        )
        return result.modified_count > 0

    @staticmethod
    async def disconnect_chat(chat_id: int) -> bool:
        """Disconnect Telegram group from room"""
        db = get_database()
        result = await db.rooms.update_one(
            {"linked_chat_id": chat_id},
            {"$set": {"linked_chat_id": None}}
        )
        return result.modified_count > 0

    @staticmethod
    async def get_all_rooms(skip: int = 0, limit: int = 50):
        """Get all rooms with pagination"""
        db = get_database()
        cursor = db.rooms.find({"is_active": True}).skip(skip).limit(limit).sort("created_at", -1)
        rooms = await cursor.to_list(length=limit)
        return [Room(**r) for r in rooms]

    @staticmethod
    async def count_rooms() -> int:
        """Count total active rooms"""
        db = get_database()
        return await db.rooms.count_documents({"is_active": True})

    @staticmethod
    async def deactivate_room(code: str):
        """Soft delete a room"""
        db = get_database()
        await db.rooms.update_one(
            {"code": code},
            {"$set": {"is_active": False}}
        )
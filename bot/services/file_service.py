from db.mongo import get_database
from bot.models.models import File
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class FileService:
    @staticmethod
    async def save_file(file_id: str, file_type: str, room_code: str, uploader_id: int,
                       file_name: Optional[str] = None, caption: Optional[str] = None,
                       tags: List[str] = None, ai_tags: List[str] = None,
                       message_id: Optional[int] = None) -> File:
        """Save file metadata to database"""
        db = get_database()
        
        file = File(
            file_id=file_id,
            file_type=file_type,
            file_name=file_name,
            caption=caption,
            uploader_id=uploader_id,
            room_code=room_code,
            tags=tags or [],
            ai_tags=ai_tags or [],
            message_id=message_id
        )
        
        await db.files.insert_one(file.model_dump())
        logger.info(f"Saved file {file_id} to room {room_code}")
        
        return file

    @staticmethod
    async def add_tags(file_id: str, tags: List[str]):
        """Add tags to a file"""
        db = get_database()
        await db.files.update_one(
            {"file_id": file_id},
            {"$addToSet": {"tags": {"$each": tags}}}
        )

    @staticmethod
    async def get_file_by_message_id(room_code: str, message_id: int) -> Optional[File]:
        """Get file by message ID in a room"""
        db = get_database()
        file_data = await db.files.find_one({"room_code": room_code, "message_id": message_id})
        return File(**file_data) if file_data else None

    @staticmethod
    async def get_files_by_room(room_code: str, skip: int = 0, limit: int = 50) -> List[File]:
        """Get all files in a room"""
        db = get_database()
        cursor = db.files.find({"room_code": room_code}).skip(skip).limit(limit).sort("created_at", -1)
        files = await cursor.to_list(length=limit)
        return [File(**f) for f in files]

    @staticmethod
    async def count_files(room_code: Optional[str] = None) -> int:
        """Count files, optionally filtered by room"""
        db = get_database()
        query = {"room_code": room_code} if room_code else {}
        return await db.files.count_documents(query)

    @staticmethod
    async def count_all_files() -> int:
        """Count all files across all rooms"""
        db = get_database()
        return await db.files.count_documents({})

    @staticmethod
    async def get_all_files(skip: int = 0, limit: int = 50):
        """Get all files with pagination"""
        db = get_database()
        cursor = db.files.find().skip(skip).limit(limit).sort("created_at", -1)
        files = await cursor.to_list(length=limit)
        return [File(**f) for f in files]
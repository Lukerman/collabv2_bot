from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Initialize MongoDB connection"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Create indexes
            await cls.create_indexes()
            
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    async def create_indexes(cls):
        """Create necessary indexes for collections"""
        if cls.db is None:  # Changed from: if not cls.db:
            return
        
        try:
            # Users indexes
            await cls.db.users.create_index("user_id", unique=True)
            await cls.db.users.create_index("username")
            
            # Rooms indexes
            await cls.db.rooms.create_index("code", unique=True)
            await cls.db.rooms.create_index("owner_id")
            await cls.db.rooms.create_index("linked_chat_id")
            
            # Files indexes
            await cls.db.files.create_index("room_code")
            await cls.db.files.create_index("uploader_id")
            await cls.db.files.create_index("tags")
            await cls.db.files.create_index([("file_name", "text"), ("caption", "text")])
            
            # AI Usage indexes
            await cls.db.ai_usage.create_index([("user_id", 1), ("date", -1)])
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:  # Changed from: if not cls.db:
            raise Exception("Database not initialized. Call connect_db() first.")
        return cls.db


# Convenience function
def get_database() -> AsyncIOMotorDatabase:
    return MongoDB.get_db()

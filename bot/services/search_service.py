from db.mongo import get_database
from bot.models.models import File
from typing import List
import logging

logger = logging.getLogger(__name__)


class SearchService:
    @staticmethod
    async def search_files(room_code: str, query: str, skip: int = 0, limit: int = 10) -> List[File]:
        """
        Search files in a room by:
        - Tags (case-insensitive partial match)
        - File name (case-insensitive partial match)
        - Caption (case-insensitive partial match)
        """
        db = get_database()
        
        # Build search query
        search_conditions = {
            "$and": [
                {"room_code": room_code},
                {
                    "$or": [
                        {"tags": {"$regex": query, "$options": "i"}},
                        {"ai_tags": {"$regex": query, "$options": "i"}},
                        {"file_name": {"$regex": query, "$options": "i"}},
                        {"caption": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }
        
        cursor = db.files.find(search_conditions).skip(skip).limit(limit).sort("created_at", -1)
        files = await cursor.to_list(length=limit)
        
        logger.info(f"Search '{query}' in room {room_code} returned {len(files)} results")
        
        return [File(**f) for f in files]

    @staticmethod
    async def count_search_results(room_code: str, query: str) -> int:
        """Count search results"""
        db = get_database()
        
        search_conditions = {
            "$and": [
                {"room_code": room_code},
                {
                    "$or": [
                        {"tags": {"$regex": query, "$options": "i"}},
                        {"ai_tags": {"$regex": query, "$options": "i"}},
                        {"file_name": {"$regex": query, "$options": "i"}},
                        {"caption": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }
        
        return await db.files.count_documents(search_conditions)
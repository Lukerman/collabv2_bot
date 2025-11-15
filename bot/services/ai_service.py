import httpx
from config import settings
from typing import List, Optional
from datetime import datetime
from db.mongo import get_database
import logging

logger = logging.getLogger(__name__)


class AIService:
    """
    Abstracted AI client that can work with Perplexity API or compatible LLMs
    """
    
    @staticmethod
    async def _call_api(messages: List[dict], max_tokens: Optional[int] = None) -> str:
        """Make API call to LLM service"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": settings.AI_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens or settings.AI_MAX_TOKENS,
                    "temperature": settings.AI_TEMPERATURE
                }
                
                headers = {
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                response = await client.post(
                    settings.AI_API_URL,
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extract response text (adjust based on API structure)
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                
                return "Unable to get AI response."
                
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            return f"Error: Unable to process AI request. {str(e)}"

    @staticmethod
    async def summarise(text: str) -> str:
        """Generate summary of text"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful study assistant. Provide clear, concise summaries of study materials."
            },
            {
                "role": "user",
                "content": f"Please provide a comprehensive summary of the following content:\n\n{text[:8000]}"
            }
        ]
        return await AIService._call_api(messages)

    @staticmethod
    async def explain(text: str) -> str:
        """Explain text in simpler terms"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful study assistant. Explain complex concepts in simple, easy-to-understand terms."
            },
            {
                "role": "user",
                "content": f"Please explain the following content in simple terms:\n\n{text[:8000]}"
            }
        ]
        return await AIService._call_api(messages)

    @staticmethod
    async def generate_mcqs(text: str, num_questions: int = 5) -> str:
        """Generate multiple choice questions"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful study assistant. Create clear, educational multiple-choice questions."
            },
            {
                "role": "user",
                "content": f"Generate {num_questions} multiple-choice questions (with 4 options each and indicate the correct answer) based on this content:\n\n{text[:8000]}"
            }
        ]
        return await AIService._call_api(messages, max_tokens=2000)

    @staticmethod
    async def suggest_tags(text: str) -> List[str]:
        """Suggest relevant tags for content"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful study assistant. Suggest relevant tags/keywords for study materials."
            },
            {
                "role": "user",
                "content": f"Suggest 3-5 relevant tags (single words or short phrases, comma-separated) for the following content:\n\n{text[:4000]}"
            }
        ]
        response = await AIService._call_api(messages, max_tokens=100)
        
        # Parse comma-separated tags
        tags = [tag.strip().lower() for tag in response.split(",")]
        return [tag for tag in tags if tag and len(tag) < 30][:5]

    @staticmethod
    async def check_rate_limit(user_id: int) -> bool:
        """Check if user has exceeded daily AI usage limit"""
        db = get_database()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        usage = await db.ai_usage.find_one({"user_id": user_id, "date": today})
        
        if not usage:
            return True  # No usage today, allowed
        
        total_count = usage.get("count", 0)
        return total_count < settings.AI_CALLS_PER_USER_PER_DAY

    @staticmethod
    async def increment_usage(user_id: int, command: str):
        """Increment AI usage counter for user"""
        db = get_database()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        await db.ai_usage.update_one(
            {"user_id": user_id, "date": today},
            {
                "$inc": {"count": 1},
                "$set": {"command": command, "created_at": datetime.utcnow()}
            },
            upsert=True
        )

    @staticmethod
    async def get_usage_count(user_id: int) -> int:
        """Get today's usage count for user"""
        db = get_database()
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        usage = await db.ai_usage.find_one({"user_id": user_id, "date": today})
        return usage.get("count", 0) if usage else 0

    @staticmethod
    async def get_total_ai_calls() -> int:
        """Get total AI calls across all users"""
        db = get_database()
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$count"}}}
        ]
        result = await db.ai_usage.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.services.user_service import UserService
from bot.services.room_service import RoomService
from bot.services.ai_service import AIService
from bot.services.file_service import FileService
import logging
import io

logger = logging.getLogger(__name__)


async def summarise_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /summarise or /summarize command"""
    await _handle_ai_command(update, context, "summarise")


async def explain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /explain command"""
    await _handle_ai_command(update, context, "explain")


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /quiz command"""
    num_questions = 5
    
    if context.args:
        try:
            num_questions = int(context.args[0])
            num_questions = max(1, min(num_questions, 10))  # Limit 1-10
        except ValueError:
            pass
    
    await _handle_ai_command(update, context, "quiz", num_questions=num_questions)


async def _handle_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             command: str, num_questions: int = 5):
    """Generic handler for AI commands"""
    user = update.effective_user
    message = update.message
    
    # Check if replying to a message
    if not message.reply_to_message:
        await message.reply_text(
            f"❌ Please reply to a message or file with `/{command}`",
            parse_mode="Markdown"
        )
        return
    
    # Check rate limit
    if not await AIService.check_rate_limit(user.id):
        usage = await AIService.get_usage_count(user.id)
        await message.reply_text(
            f"❌ Daily AI limit reached ({usage} calls).\n"
            "Try again tomorrow or contact admin."
        )
        return
    
    # Extract text
    replied_msg = message.reply_to_message
    text = await _extract_text_from_message(replied_msg, context)
    
    if not text:
        await message.reply_text(
            "❌ Could not extract text from this message.\n"
            "Make sure it's a text message or supported document."
        )
        return
    
    # Show processing message
    processing_msg = await message.reply_text("🤖 Processing with AI... Please wait.")
    
    try:
        # Call appropriate AI service
        if command == "summarise":
            result = await AIService.summarise(text)
        elif command == "explain":
            result = await AIService.explain(text)
        elif command == "quiz":
            result = await AIService.generate_mcqs(text, num_questions)
        else:
            result = "Unknown command"
        
        # Increment usage
        await AIService.increment_usage(user.id, command)
        
        # Send result
        await processing_msg.edit_text(
            f"✅ **AI {command.title()} Result:**\n\n{result}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"AI command failed: {e}")
        await processing_msg.edit_text(
            f"❌ An error occurred while processing your request.\n"
            f"Error: {str(e)}"
        )


async def _extract_text_from_message(message, context) -> str:
    """Extract text from a message (text, caption, or document)"""
    # Direct text
    if message.text:
        return message.text
    
    # Caption
    if message.caption:
        return message.caption
    
    # Document - try to extract text
    if message.document:
        try:
            file = await context.bot.get_file(message.document.file_id)
            file_bytes = io.BytesIO()
            await file.download_to_memory(file_bytes)
            file_bytes.seek(0)
            
            # Try to read as text
            if message.document.file_name.endswith('.txt'):
                return file_bytes.read().decode('utf-8', errors='ignore')
            
            # Basic PDF support (requires PyPDF2)
            if message.document.file_name.endswith('.pdf'):
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(file_bytes)
                    text = ""
                    for page in pdf_reader.pages[:10]:  # Limit to first 10 pages
                        text += page.extract_text()
                    return text
                except Exception as e:
                    logger.error(f"PDF extraction failed: {e}")
                    return None
            
        except Exception as e:
            logger.error(f"Document text extraction failed: {e}")
            return None
    
    return None


# Handler registration
ai_handlers = [
    CommandHandler("summarise", summarise_command),
    CommandHandler("summarize", summarise_command),
    CommandHandler("explain", explain_command),
    CommandHandler("quiz", quiz_command),
]
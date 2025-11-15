from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.services.user_service import UserService
from bot.services.room_service import RoomService
from bot.services.file_service import FileService
from bot.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads"""
    user = update.effective_user
    message = update.message
    document = message.document
    
    # Determine room
    room_code = await _get_room_for_message(update, user.id)
    
    if not room_code:
        await message.reply_text(
            "❌ Please join or create a room first before uploading files!\n"
            "Use /create_room or /join_room <CODE>"
        )
        return
    
    # Save file
    caption = message.caption or ""
    file = await FileService.save_file(
        file_id=document.file_id,
        file_type="document",
        room_code=room_code,
        uploader_id=user.id,
        file_name=document.file_name,
        caption=caption,
        message_id=message.message_id
    )
    
    # Optionally suggest tags using AI
    if caption:
        try:
            suggested_tags = await AIService.suggest_tags(caption)
            if suggested_tags:
                await FileService.add_tags(document.file_id, suggested_tags)
                await message.reply_text(
                    f"✅ File uploaded successfully!\n\n"
                    f"📎 **File:** {document.file_name}\n"
                    f"🏷️ **AI-suggested tags:** {', '.join(suggested_tags)}\n\n"
                    f"Reply to this file with `/add_tags` to add more tags.",
                    parse_mode="Markdown"
                )
                return
        except Exception as e:
            logger.error(f"Tag suggestion failed: {e}")
    
    await message.reply_text(
        f"✅ File uploaded successfully!\n\n"
        f"📎 **File:** {document.file_name}\n"
        f"Reply to this file with `/add_tags tag1, tag2` to organize it.",
        parse_mode="Markdown"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    user = update.effective_user
    message = update.message
    photo = message.photo[-1]  # Get highest resolution
    
    # Determine room
    room_code = await _get_room_for_message(update, user.id)
    
    if not room_code:
        await message.reply_text(
            "❌ Please join or create a room first before uploading files!\n"
            "Use /create_room or /join_room <CODE>"
        )
        return
    
    # Save file
    caption = message.caption or "Photo"
    await FileService.save_file(
        file_id=photo.file_id,
        file_type="photo",
        room_code=room_code,
        uploader_id=user.id,
        file_name="photo.jpg",
        caption=caption,
        message_id=message.message_id
    )
    
    await message.reply_text(
        "✅ Photo uploaded successfully!\n"
        "Reply with `/add_tags` to add tags.",
        parse_mode="Markdown"
    )


async def add_tags_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add_tags command (must reply to a file)"""
    user = update.effective_user
    message = update.message
    
    if not message.reply_to_message:
        await message.reply_text(
            "❌ Please reply to a file with `/add_tags tag1, tag2, tag3`",
            parse_mode="Markdown"
        )
        return
    
    if not context.args:
        await message.reply_text(
            "❌ Please provide tags:\n"
            "`/add_tags tag1, tag2, tag3`",
            parse_mode="Markdown"
        )
        return
    
    # Get room
    room_code = await _get_room_for_message(update, user.id)
    if not room_code:
        await message.reply_text("❌ You're not in any room.")
        return
    
    # Parse tags
    tags_text = " ".join(context.args)
    tags = [tag.strip().lower() for tag in tags_text.split(",")]
    tags = [tag for tag in tags if tag]  # Remove empty
    
    if not tags:
        await message.reply_text("❌ No valid tags provided.")
        return
    
    # Get file
    replied_msg = message.reply_to_message
    file_id = None
    
    if replied_msg.document:
        file_id = replied_msg.document.file_id
    elif replied_msg.photo:
        file_id = replied_msg.photo[-1].file_id
    
    if not file_id:
        await message.reply_text("❌ Replied message doesn't contain a supported file.")
        return
    
    # Add tags
    await FileService.add_tags(file_id, tags)
    
    await message.reply_text(
        f"✅ Added tags: {', '.join(tags)}",
        parse_mode="Markdown"
    )


async def _get_room_for_message(update: Update, user_id: int) -> str:
    """Determine which room a message belongs to"""
    chat = update.effective_chat
    
    # If private chat, use user's current room
    if chat.type == "private":
        user_data = await UserService.get_user(user_id)
        return user_data.current_room_code if user_data else None
    
    # If group chat, find linked room
    room = await RoomService.get_room_by_chat_id(chat.id)
    return room.code if room else None


# Handler registration
file_handlers = [
    MessageHandler(filters.Document.ALL, handle_document),
    MessageHandler(filters.PHOTO, handle_photo),
    CommandHandler("add_tags", add_tags_command),
]
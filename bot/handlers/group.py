from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ChatType
from bot.services.room_service import RoomService
import logging

logger = logging.getLogger(__name__)


async def connect_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /connect_room command in groups"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Only works in groups
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "❌ This command only works in group chats."
        )
        return
    
    # Check if user is admin
    admins = await context.bot.get_chat_administrators(chat.id)
    is_admin = any(admin.user.id == user.id for admin in admins)
    
    if not is_admin:
        await update.message.reply_text(
            "❌ Only group administrators can link rooms."
        )
        return
    
    # Get room code
    if not context.args:
        await update.message.reply_text(
            "Please provide a room code:\n"
            "`/connect_room <CODE>`",
            parse_mode="Markdown"
        )
        return
    
    code = context.args[0].upper()
    
    # Check if room exists
    room = await RoomService.get_room(code)
    if not room:
        await update.message.reply_text(
            f"❌ Room `{code}` not found.",
            parse_mode="Markdown"
        )
        return
    
    # Link room
    success = await RoomService.link_chat(code, chat.id, user.id)
    
    if success:
        await update.message.reply_text(
            f"✅ This group is now linked to room:\n\n"
            f"**Room Name:** {room.name}\n"
            f"**Room Code:** `{code}`\n\n"
            f"Members can now upload files and use AI commands here!",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Failed to link room. You must be the room owner."
        )


async def disconnect_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /disconnect_room command in groups"""
    chat = update.effective_chat
    user = update.effective_user
    
    # Only works in groups
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "❌ This command only works in group chats."
        )
        return
    
    # Check if user is admin
    admins = await context.bot.get_chat_administrators(chat.id)
    is_admin = any(admin.user.id == user.id for admin in admins)
    
    if not is_admin:
        await update.message.reply_text(
            "❌ Only group administrators can disconnect rooms."
        )
        return
    
    # Disconnect room
    success = await RoomService.disconnect_chat(chat.id)
    
    if success:
        await update.message.reply_text(
            "✅ This group has been disconnected from the room."
        )
    else:
        await update.message.reply_text(
            "❌ This group is not linked to any room."
        )


# Handler registration
group_handlers = [
    CommandHandler("connect_room", connect_room_command),
    CommandHandler("disconnect_room", disconnect_room_command),
]
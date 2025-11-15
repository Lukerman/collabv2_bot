from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from bot.services.user_service import UserService
from bot.services.room_service import RoomService
import logging

logger = logging.getLogger(__name__)

# Conversation states
ROOM_NAME, ROOM_DESCRIPTION = range(2)


async def create_room_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start room creation conversation"""
    await update.message.reply_text(
        "Let's create a new study room! 🎓\n\n"
        "What would you like to name your room?\n"
        "(Send /cancel to abort)"
    )
    return ROOM_NAME


async def create_room_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive room name"""
    context.user_data['room_name'] = update.message.text
    
    await update.message.reply_text(
        f"Great! Room name: *{update.message.text}*\n\n"
        "Now, add a description (or send /skip):",
        parse_mode="Markdown"
    )
    return ROOM_DESCRIPTION


async def create_room_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive room description and create room"""
    user = update.effective_user
    room_name = context.user_data['room_name']
    description = update.message.text
    
    # Create room
    room = await RoomService.create_room(
        name=room_name,
        owner_id=user.id,
        description=description
    )
    
    # Update user's current room
    await UserService.update_current_room(user.id, room.code)
    
    await update.message.reply_text(
        f"✅ Room created successfully!\n\n"
        f"**Room Name:** {room.name}\n"
        f"**Room Code:** `{room.code}`\n"
        f"**Description:** {room.description or 'None'}\n\n"
        f"Share this code with others so they can join!\n"
        f"You can now upload files and use all features.",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def create_room_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip description and create room"""
    user = update.effective_user
    room_name = context.user_data['room_name']
    
    # Create room without description
    room = await RoomService.create_room(
        name=room_name,
        owner_id=user.id
    )
    
    # Update user's current room
    await UserService.update_current_room(user.id, room.code)
    
    await update.message.reply_text(
        f"✅ Room created successfully!\n\n"
        f"**Room Name:** {room.name}\n"
        f"**Room Code:** `{room.code}`\n\n"
        f"Share this code with others so they can join!",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Room creation cancelled.")
    return ConversationHandler.END


async def join_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /join_room command"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a room code:\n"
            "`/join_room <CODE>`",
            parse_mode="Markdown"
        )
        return
    
    code = context.args[0].upper()
    
    # Check if room exists
    room = await RoomService.get_room(code)
    if not room:
        await update.message.reply_text(
            f"❌ Room with code `{code}` not found.\n"
            "Please check the code and try again.",
            parse_mode="Markdown"
        )
        return
    
    # Join room
    await RoomService.join_room(code, user.id)
    await UserService.update_current_room(user.id, code)
    
    await update.message.reply_text(
        f"✅ Successfully joined room!\n\n"
        f"**Room Name:** {room.name}\n"
        f"**Room Code:** `{room.code}`\n"
        f"**Description:** {room.description or 'None'}\n"
        f"**Members:** {len(room.members) + 1}\n\n"
        f"You can now upload files and use all features.",
        parse_mode="Markdown"
    )


async def my_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /my_room command"""
    user = update.effective_user
    
    user_data = await UserService.get_user(user.id)
    
    if not user_data or not user_data.current_room_code:
        await update.message.reply_text(
            "❌ You're not in any room.\n\n"
            "Create one with /create_room or join with /join_room"
        )
        return
    
    room = await RoomService.get_room(user_data.current_room_code)
    
    if not room:
        await update.message.reply_text("❌ Current room not found.")
        return
    
    is_owner = room.owner_id == user.id
    
    await update.message.reply_text(
        f"📚 **Your Current Room**\n\n"
        f"**Name:** {room.name}\n"
        f"**Code:** `{room.code}`\n"
        f"**Description:** {room.description or 'None'}\n"
        f"**Members:** {len(room.members)}\n"
        f"**Your Role:** {'👑 Owner' if is_owner else '👤 Member'}\n"
        f"**Linked to Group:** {'Yes' if room.linked_chat_id else 'No'}",
        parse_mode="Markdown"
    )


async def leave_room_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leave_room command"""
    user = update.effective_user
    
    user_data = await UserService.get_user(user.id)
    
    if not user_data or not user_data.current_room_code:
        await update.message.reply_text("❌ You're not in any room.")
        return
    
    code = user_data.current_room_code
    
    # Leave room
    await RoomService.leave_room(code, user.id)
    await UserService.update_current_room(user.id, None)
    
    await update.message.reply_text(
        f"✅ You have left the room `{code}`.",
        parse_mode="Markdown"
    )


# Handler registration
create_room_conv = ConversationHandler(
    entry_points=[CommandHandler("create_room", create_room_start)],
    states={
        ROOM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_room_name)],
        ROOM_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, create_room_description),
            CommandHandler("skip", create_room_skip)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

room_handlers = [
    create_room_conv,
    CommandHandler("join_room", join_room_command),
    CommandHandler("my_room", my_room_command),
    CommandHandler("leave_room", leave_room_command),
]
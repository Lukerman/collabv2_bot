from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.services.user_service import UserService
from bot.services.room_service import RoomService
from bot.services.search_service import SearchService
import logging

logger = logging.getLogger(__name__)

RESULTS_PER_PAGE = 5


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a search query:\n"
            "`/search <keywords or tags>`",
            parse_mode="Markdown"
        )
        return
    
    query = " ".join(context.args)
    
    # Get room
    chat = update.effective_chat
    if chat.type == "private":
        user_data = await UserService.get_user(user.id)
        room_code = user_data.current_room_code if user_data else None
    else:
        room = await RoomService.get_room_by_chat_id(chat.id)
        room_code = room.code if room else None
    
    if not room_code:
        await update.message.reply_text(
            "❌ You need to be in a room to search.\n"
            "Use /create_room or /join_room"
        )
        return
    
    # Search
    files = await SearchService.search_files(room_code, query, skip=0, limit=RESULTS_PER_PAGE)
    total = await SearchService.count_search_results(room_code, query)
    
    if not files:
        await update.message.reply_text(
            f"🔍 No results found for: *{query}*",
            parse_mode="Markdown"
        )
        return
    
    # Display results
    await _display_search_results(update, files, query, room_code, page=0, total=total)


async def _display_search_results(update, files, query, room_code, page, total):
    """Display search results with pagination"""
    result_text = f"🔍 **Search Results for:** {query}\n"
    result_text += f"Found {total} file(s)\n\n"
    
    for idx, file in enumerate(files, start=page * RESULTS_PER_PAGE + 1):
        tags_display = ", ".join(file.tags + file.ai_tags) if (file.tags or file.ai_tags) else "No tags"
        result_text += f"{idx}. 📎 **{file.file_name or 'Unnamed'}**\n"
        result_text += f"   🏷️ {tags_display}\n"
        if file.caption:
            result_text += f"   💬 {file.caption[:50]}...\n"
        result_text += "\n"
    
    # Pagination buttons
    keyboard = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"search_prev_{page}_{query}_{room_code}"))
    
    if (page + 1) * RESULTS_PER_PAGE < total:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"search_next_{page}_{query}_{room_code}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            result_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            result_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def search_pagination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination callbacks"""
    query_data = update.callback_query
    await query_data.answer()
    
    data_parts = query_data.data.split("_")
    direction = data_parts[1]  # prev or next
    current_page = int(data_parts[2])
    query = data_parts[3]
    room_code = data_parts[4]
    
    new_page = current_page - 1 if direction == "prev" else current_page + 1
    
    # Get results for new page
    files = await SearchService.search_files(
        room_code, 
        query, 
        skip=new_page * RESULTS_PER_PAGE, 
        limit=RESULTS_PER_PAGE
    )
    total = await SearchService.count_search_results(room_code, query)
    
    await _display_search_results(update, files, query, room_code, new_page, total)


# Handler registration
search_handlers = [
    CommandHandler("search", search_command),
    CallbackQueryHandler(search_pagination_callback, pattern="^search_(prev|next)_"),
]
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Register or get user
    await UserService.get_or_create_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    welcome_message = f"""
🎓 **Welcome to CollaLearn!**

Hello {user.first_name}! CollaLearn is your AI-powered collaborative study platform.

**What you can do:**
📚 Create or join study rooms
📎 Upload study materials (PDFs, images, notes)
🔍 Search files by tags and keywords
🤖 Use AI to summarize, explain, and quiz yourself
👥 Collaborate in groups

**Quick Start:**
1️⃣ Create a room: /create_room
2️⃣ Upload your files
3️⃣ Tag them for easy search
4️⃣ Use AI commands on your materials

Type /help for detailed command list.
"""
    
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📖 **CollaLearn Commands**

**Room Management:**
• `/create_room` - Create a new study room
• `/join_room <CODE>` - Join an existing room
• `/my_room` - View your current room info
• `/leave_room` - Leave current room

**File Management:**
• Send any file to upload (PDF, image, doc)
• `/add_tags <tags>` - Reply to a file to add tags
• `/search <query>` - Search files in current room

**AI Features:**
• `/summarise` or `/summarize` - Reply to content to get summary
• `/explain` - Reply to content for simple explanation
• `/quiz [number]` - Generate MCQs from content

**Group Features (for group admins):**
• `/connect_room <CODE>` - Link this group to a room
• `/disconnect_room` - Unlink group from room

**Other:**
• `/help` - Show this help message
• `/start` - Restart bot

**Tips:**
✨ Reply to any file or message with AI commands
🏷️ Use tags like: "chapter1, physics, important"
🔍 Search by tags, filenames, or content
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


# Handler registration
start_handlers = [
    CommandHandler("start", start_command),
    CommandHandler("help", help_command),
]
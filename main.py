import asyncio
import logging
from telegram.ext import Application
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from threading import Thread

from config import settings
from db.mongo import MongoDB
from admin.routes import router as admin_router

# Import all handlers
from bot.handlers.start import start_handlers
from bot.handlers.room import room_handlers
from bot.handlers.file import file_handlers
from bot.handlers.search import search_handlers
from bot.handlers.ai import ai_handlers
from bot.handlers.group import group_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO if not settings.DEBUG else logging.DEBUG
)
logger = logging.getLogger(__name__)


# Telegram Bot Application
telegram_app = None


async def setup_bot():
    """Initialize and setup the Telegram bot"""
    global telegram_app
    
    # Create application
    telegram_app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Register all handlers
    for handler in start_handlers:
        telegram_app.add_handler(handler)
    
    for handler in room_handlers:
        telegram_app.add_handler(handler)
    
    for handler in file_handlers:
        telegram_app.add_handler(handler)
    
    for handler in search_handlers:
        telegram_app.add_handler(handler)
    
    for handler in ai_handlers:
        telegram_app.add_handler(handler)
    
    for handler in group_handlers:
        telegram_app.add_handler(handler)
    
    logger.info("Telegram bot handlers registered successfully")
    
    return telegram_app


async def start_bot():
    """Start the Telegram bot in polling mode"""
    global telegram_app
    
    logger.info("Starting Telegram bot...")
    
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(drop_pending_updates=True)
    
    logger.info("Telegram bot started successfully")


async def stop_bot():
    """Stop the Telegram bot"""
    global telegram_app
    
    if telegram_app:
        logger.info("Stopping Telegram bot...")
        await telegram_app.updater.stop()
        await telegram_app.stop()
        await telegram_app.shutdown()
        logger.info("Telegram bot stopped")


# FastAPI Application for Admin Panel
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting CollaLearn application...")
    
    # Connect to MongoDB
    await MongoDB.connect_db()
    
    # Setup and start bot
    await setup_bot()
    asyncio.create_task(start_bot())
    
    logger.info("CollaLearn started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CollaLearn...")
    await stop_bot()
    await MongoDB.close_db()
    logger.info("CollaLearn shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="CollaLearn Admin Panel",
    description="Admin panel for CollaLearn Telegram bot",
    version="1.0.0",
    lifespan=lifespan
)

# Include admin router
app.include_router(admin_router)


@app.get("/")
async def root():
    """Root endpoint - redirect to admin"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CollaLearn",
        "version": "1.0.0"
    }


def main():
    """Main entry point"""
    logger.info(f"""
    ╔══════════════════════════════════════╗
    ║       CollaLearn Starting...         ║
    ║   AI-Powered Study Rooms on Telegram║
    ╚══════════════════════════════════════╝
    """)
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.ADMIN_PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )


if __name__ == "__main__":
    main()
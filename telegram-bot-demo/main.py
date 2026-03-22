"""Entry point for the Task Manager Telegram Bot."""

import logging
import sys

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.handlers.common import help_handler, main_menu_callback, start_handler
from bot.handlers.errors import error_handler
from bot.handlers.tasks import (
    build_task_conversation,
    complete_task_callback,
    delete_task_callback,
    filter_tasks_callback,
    list_tasks_callback,
    list_tasks_command,
    start_task_callback,
    stats_callback,
    task_detail_callback,
)
from bot.models.database import init_database
from bot.services.task_service import TaskService
from bot.services.user_service import UserService
from config import get_config


def setup_logging(level: str) -> None:
    """Configure logging with console and file outputs."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
    logging.basicConfig(level=getattr(logging, level), format=log_format, handlers=handlers)
    logging.getLogger("httpx").setLevel(logging.WARNING)


async def post_init(application) -> None:
    """Run after the application is initialized — set up DB and services."""
    config = application.bot_data["config"]
    await init_database(config.database_path)

    application.bot_data["user_service"] = UserService(config.database_path)
    application.bot_data["task_service"] = TaskService(config.database_path)


def main() -> None:
    """Build the application, register handlers, and start polling."""
    config = get_config()
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting Task Manager Bot...")

    app = ApplicationBuilder().token(config.bot_token).post_init(post_init).build()
    app.bot_data["config"] = config

    # Command handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("tasks", list_tasks_command))

    # Task creation conversation
    app.add_handler(build_task_conversation())

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(list_tasks_callback, pattern="^task_list$"))
    app.add_handler(CallbackQueryHandler(filter_tasks_callback, pattern="^filter_"))
    app.add_handler(CallbackQueryHandler(task_detail_callback, pattern="^task_detail_"))
    app.add_handler(CallbackQueryHandler(complete_task_callback, pattern="^complete_"))
    app.add_handler(CallbackQueryHandler(start_task_callback, pattern="^start_"))
    app.add_handler(CallbackQueryHandler(delete_task_callback, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(stats_callback, pattern="^stats$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^help$"))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("Bot is ready. Polling for updates...")
    app.run_polling()


if __name__ == "__main__":
    main()

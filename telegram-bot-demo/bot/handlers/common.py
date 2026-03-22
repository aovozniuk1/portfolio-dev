"""Common command handlers: /start, /help, main menu."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.inline import main_menu_keyboard
from bot.services.user_service import UserService

logger = logging.getLogger(__name__)

HELP_TEXT = (
    "Task Manager Bot\n"
    "================\n\n"
    "Commands:\n"
    "  /start  - Start the bot and open main menu\n"
    "  /help   - Show this help message\n"
    "  /tasks  - List your tasks\n"
    "  /add    - Add a new task\n"
    "  /stats  - View your statistics\n\n"
    "You can also use the inline buttons for navigation."
)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command. Registers user and shows the main menu."""
    user = update.effective_user
    if not user:
        return

    user_service: UserService = context.bot_data["user_service"]
    await user_service.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    await update.message.reply_text(
        f"Welcome, {user.first_name}!\n\nI'm your personal task manager. "
        "Use the buttons below or type /help to see available commands.",
        reply_markup=main_menu_keyboard(),
    )
    logger.info("User %d started the bot", user.id)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    await update.message.reply_text(HELP_TEXT)


async def main_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the 'main_menu' callback to redisplay the menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Main Menu - choose an action:",
        reply_markup=main_menu_keyboard(),
    )

"""Global error handler for the bot."""

import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify the user when something goes wrong.

    This handler is attached to the application-level error hook so that
    unhandled exceptions in any handler are caught gracefully.
    """
    logger.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)
    logger.debug("Full traceback:\n%s", tb_string)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "An unexpected error occurred. Please try again later."
        )

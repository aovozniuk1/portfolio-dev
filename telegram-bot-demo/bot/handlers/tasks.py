"""Task management handlers: add, list, detail, complete, delete."""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.keyboards.inline import (
    filter_keyboard,
    main_menu_keyboard,
    priority_keyboard,
    task_actions_keyboard,
    task_list_keyboard,
)
from bot.models.task import TaskPriority, TaskStatus
from bot.services.task_service import TaskService
from bot.services.user_service import UserService

logger = logging.getLogger(__name__)

# Conversation states
WAITING_TITLE, WAITING_DESCRIPTION, WAITING_PRIORITY = range(3)


def _get_services(context: ContextTypes.DEFAULT_TYPE) -> tuple:
    """Extract services from bot_data."""
    return context.bot_data["user_service"], context.bot_data["task_service"]


async def _get_user_id(
    telegram_id: int, user_service: UserService
) -> Optional[int]:
    """Look up internal user ID from Telegram ID."""
    user = await user_service.get_by_telegram_id(telegram_id)
    return user.id if user else None


# --- Add task conversation ---


async def add_task_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Begin the add-task conversation. Prompt for a title."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Enter the task title:")
    else:
        await update.message.reply_text("Enter the task title:")
    return WAITING_TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the title and ask for an optional description."""
    context.user_data["new_task_title"] = update.message.text.strip()
    await update.message.reply_text(
        "Enter a description (or send /skip to skip):"
    )
    return WAITING_DESCRIPTION


async def receive_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Store description and ask for priority."""
    text = update.message.text.strip()
    if text.lower() == "/skip":
        context.user_data["new_task_description"] = None
    else:
        context.user_data["new_task_description"] = text

    await update.message.reply_text(
        "Select priority:", reply_markup=priority_keyboard()
    )
    return WAITING_PRIORITY


async def receive_priority(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Create the task with selected priority."""
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "cancel":
        await query.edit_message_text(
            "Task creation cancelled.", reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    priority_value = data.replace("priority_", "")
    priority = TaskPriority(priority_value)

    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)
    if not user_id:
        await query.edit_message_text("Please run /start first.")
        return ConversationHandler.END

    task = await task_service.create(
        user_id=user_id,
        title=context.user_data["new_task_title"],
        description=context.user_data.get("new_task_description"),
        priority=priority,
    )

    await query.edit_message_text(
        f"Task created: #{task.id} - {task.title}\n"
        f"Priority: {task.priority_label}",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def cancel_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Cancel the current conversation."""
    await update.message.reply_text(
        "Cancelled.", reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


# --- Task listing and details ---


async def list_tasks_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show the task filter menu."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Filter tasks by status:", reply_markup=filter_keyboard()
    )


async def list_tasks_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /tasks command."""
    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)
    if not user_id:
        await update.message.reply_text("Please run /start first.")
        return

    tasks = await task_service.get_by_user(user_id)
    if not tasks:
        await update.message.reply_text(
            "You have no tasks yet.", reply_markup=main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        f"Your tasks ({len(tasks)}):", reply_markup=task_list_keyboard(tasks)
    )


async def filter_tasks_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Filter tasks by selected status."""
    query = update.callback_query
    await query.answer()

    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)
    if not user_id:
        await query.edit_message_text("Please run /start first.")
        return

    filter_value = query.data.replace("filter_", "")
    status = None if filter_value == "all" else TaskStatus(filter_value)

    tasks = await task_service.get_by_user(user_id, status=status)
    if not tasks:
        label = status.value if status else "any status"
        await query.edit_message_text(
            f"No tasks found with {label}.",
            reply_markup=filter_keyboard(),
        )
        return

    await query.edit_message_text(
        f"Tasks ({len(tasks)}):", reply_markup=task_list_keyboard(tasks)
    )


async def task_detail_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show details and actions for a specific task."""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.replace("task_detail_", ""))

    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)
    task = await task_service.get_by_id(task_id, user_id) if user_id else None

    if not task:
        await query.edit_message_text("Task not found.", reply_markup=main_menu_keyboard())
        return

    desc = task.description or "No description"
    text = (
        f"Task #{task.id}: {task.title}\n\n"
        f"Status: {task.status.value}\n"
        f"Priority: {task.priority_label}\n"
        f"Description: {desc}\n"
        f"Created: {task.created_at:%Y-%m-%d %H:%M}"
    )
    if task.completed_at:
        text += f"\nCompleted: {task.completed_at:%Y-%m-%d %H:%M}"

    await query.edit_message_text(text, reply_markup=task_actions_keyboard(task))


# --- Task actions ---


async def complete_task_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Mark a task as completed."""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.replace("complete_", ""))
    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)

    task = await task_service.update_status(task_id, user_id, TaskStatus.COMPLETED)
    if task:
        await query.edit_message_text(
            f"Task #{task.id} marked as completed.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await query.edit_message_text("Task not found.", reply_markup=main_menu_keyboard())


async def start_task_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Move a task to in_progress status."""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.replace("start_", ""))
    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)

    task = await task_service.update_status(task_id, user_id, TaskStatus.IN_PROGRESS)
    if task:
        await query.edit_message_text(
            f"Task #{task.id} is now in progress.",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await query.edit_message_text("Task not found.", reply_markup=main_menu_keyboard())


async def delete_task_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Delete a task."""
    query = update.callback_query
    await query.answer()

    task_id = int(query.data.replace("delete_", ""))
    user_service, task_service = _get_services(context)
    user_id = await _get_user_id(update.effective_user.id, user_service)

    deleted = await task_service.delete(task_id, user_id)
    msg = f"Task #{task_id} deleted." if deleted else "Task not found."
    await query.edit_message_text(msg, reply_markup=main_menu_keyboard())


# --- Stats ---


async def stats_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show task statistics."""
    query = update.callback_query
    await query.answer()

    user_service: UserService = context.bot_data["user_service"]
    user_id = await _get_user_id(update.effective_user.id, user_service)
    if not user_id:
        await query.edit_message_text("Please run /start first.")
        return

    stats = await user_service.get_user_stats(user_id)
    text = (
        "Your Statistics\n"
        "===============\n\n"
        f"Total tasks:   {stats['total']}\n"
        f"Pending:       {stats['pending']}\n"
        f"In progress:   {stats['in_progress']}\n"
        f"Completed:     {stats['completed']}\n"
    )
    if stats["total"] > 0:
        pct = (stats["completed"] / stats["total"]) * 100
        text += f"\nCompletion rate: {pct:.0f}%"

    await query.edit_message_text(text, reply_markup=main_menu_keyboard())


def build_task_conversation() -> ConversationHandler:
    """Build and return the task-creation ConversationHandler."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_task_start, pattern="^task_add$"),
            CommandHandler("add", add_task_start),
        ],
        states={
            WAITING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title),
            ],
            WAITING_DESCRIPTION: [
                MessageHandler(filters.TEXT, receive_description),
            ],
            WAITING_PRIORITY: [
                CallbackQueryHandler(receive_priority, pattern="^(priority_|cancel)"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_conversation),
        ],
    )

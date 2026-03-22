"""Inline keyboard builders for the bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.models.task import Task, TaskPriority, TaskStatus


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    buttons = [
        [
            InlineKeyboardButton("Add Task", callback_data="task_add"),
            InlineKeyboardButton("My Tasks", callback_data="task_list"),
        ],
        [
            InlineKeyboardButton("Statistics", callback_data="stats"),
            InlineKeyboardButton("Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def priority_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard for selecting task priority."""
    buttons = [
        [
            InlineKeyboardButton("Low", callback_data=f"priority_{TaskPriority.LOW.value}"),
            InlineKeyboardButton("Medium", callback_data=f"priority_{TaskPriority.MEDIUM.value}"),
            InlineKeyboardButton("High", callback_data=f"priority_{TaskPriority.HIGH.value}"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(buttons)


def task_actions_keyboard(task: Task) -> InlineKeyboardMarkup:
    """Build action buttons for a specific task."""
    buttons = []

    if task.status != TaskStatus.COMPLETED:
        buttons.append(
            InlineKeyboardButton("Complete", callback_data=f"complete_{task.id}")
        )
    if task.status == TaskStatus.PENDING:
        buttons.append(
            InlineKeyboardButton("Start", callback_data=f"start_{task.id}")
        )

    buttons.append(
        InlineKeyboardButton("Delete", callback_data=f"delete_{task.id}")
    )

    rows = [buttons]
    rows.append([InlineKeyboardButton("Back to list", callback_data="task_list")])
    return InlineKeyboardMarkup(rows)


def task_list_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    """Build a scrollable list of tasks as inline buttons."""
    buttons = []
    for task in tasks[:10]:
        label = f"{task.status_emoji} {task.title[:30]}"
        buttons.append(
            [InlineKeyboardButton(label, callback_data=f"task_detail_{task.id}")]
        )

    buttons.append([InlineKeyboardButton("Back to menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)


def filter_keyboard() -> InlineKeyboardMarkup:
    """Build a keyboard to filter tasks by status."""
    buttons = [
        [
            InlineKeyboardButton("All", callback_data="filter_all"),
            InlineKeyboardButton("Pending", callback_data="filter_pending"),
        ],
        [
            InlineKeyboardButton("In Progress", callback_data="filter_in_progress"),
            InlineKeyboardButton("Completed", callback_data="filter_completed"),
        ],
        [InlineKeyboardButton("Back to menu", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(buttons)

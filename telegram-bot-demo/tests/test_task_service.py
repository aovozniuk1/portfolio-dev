import pytest
import asyncio

from bot.models.database import init_database, get_connection
from bot.models.task import TaskStatus, TaskPriority
from bot.services.task_service import TaskService


DB_PATH = ":memory:"


@pytest.fixture()
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def service(db_path):
    await init_database(db_path)
    # insert a test user so foreign key works
    conn = await get_connection(db_path)
    await conn.execute(
        "INSERT INTO users (telegram_id, first_name) VALUES (?, ?)",
        (12345, "TestUser"),
    )
    await conn.commit()
    await conn.close()
    return TaskService(db_path)


@pytest.mark.asyncio
async def test_create_task(service):
    svc = await service
    task = await svc.create(user_id=1, title="Buy groceries")
    assert task.title == "Buy groceries"
    assert task.status == TaskStatus.PENDING
    assert task.priority == TaskPriority.MEDIUM


@pytest.mark.asyncio
async def test_list_tasks_for_user(service):
    svc = await service
    await svc.create(user_id=1, title="Task A")
    await svc.create(user_id=1, title="Task B")

    tasks = await svc.get_by_user(user_id=1)
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_complete_task(service):
    svc = await service
    task = await svc.create(user_id=1, title="Finish report")
    updated = await svc.update_status(task.id, user_id=1, new_status=TaskStatus.COMPLETED)

    assert updated is not None
    assert updated.status == TaskStatus.COMPLETED


@pytest.mark.asyncio
async def test_delete_task(service):
    svc = await service
    task = await svc.create(user_id=1, title="Temp task")
    deleted = await svc.delete(task.id, user_id=1)
    assert deleted is True

    remaining = await svc.get_by_user(user_id=1)
    assert len(remaining) == 0

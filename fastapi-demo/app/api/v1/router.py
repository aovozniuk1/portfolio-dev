"""Aggregate all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, tasks, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)

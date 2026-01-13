from aiogram import Router

from .handlers.registration import router as start_router
from .handlers.lightning_handlers import router as lightning_router


def build_router() -> Router:
    root = Router(name="root")
    root.include_router(start_router)
    root.include_router(lightning_router)
    return root

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db import session_manager, DB_URL


def init_app(init_db=True):
    lifespan = None

    if init_db:
        session_manager.init(host=DB_URL)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if session_manager._engine is not None:
                await session_manager.close()

    server = FastAPI(
        title="Trace",
        summary="a simple tcp traceroute api.",
        lifespan=lifespan,
    )

    from app.api.main import api_router

    server.include_router(api_router, prefix="/api")

    return server

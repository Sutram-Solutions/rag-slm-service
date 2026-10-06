"""FastAPI application factory."""

import asyncio
import sys

from fastapi import FastAPI

# Must run before any async database connection is created.
# Windows defaults to ProactorEventLoop; psycopg's async mode needs a selector loop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Service", version="0.1.0")
    return app


app = create_app()

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api_handler import APIHandler
from .runtime import Runtime

# Setup runtime
runtime = Runtime()
runtime.load_config()
runtime.connect_database(runtime.get_config().database_file, check_same_thread=False)

routes = FastAPI(title="wypt API", version="1")


@routes.get("/database/{table}", response_class=JSONResponse)
def get_table(
    table: str,
    next: str = "",  # noqa: A002
    limit: int = 100,
) -> dict[str, str]:
    handler = APIHandler(runtime.get_database())
    return handler.get_table_dct(table, next, limit)

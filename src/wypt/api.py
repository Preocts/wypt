from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api_handler import APIHandler
from .runtime import Runtime

# Setup runtime
runtime = Runtime()
runtime.load_config()
runtime.set_database(runtime.get_config().database_file)

routes = FastAPI(title="wypt API", version="1")


@routes.get("/database/{table}", response_class=JSONResponse)
def get_table(
    table: str,
    next: str = "",  # noqa: A002
    limit: int = 100,
) -> dict[str, str]:
    handler = APIHandler(runtime.get_database())
    return handler.get_table_dct(table, next, limit)


@routes.delete("/database/{table}", response_class=JSONResponse)
def delete_table_row(table: str, keys: str) -> dict[str, str]:
    handler = APIHandler(runtime.get_database())
    return handler.delete_table_rows(table, keys)

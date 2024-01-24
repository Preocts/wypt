from __future__ import annotations

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .api_handler import APIHandler
from .runtime import Runtime

# Setup runtime
runtime = Runtime()
runtime.load_config()
runtime.set_database(runtime.get_config().database_file)

# Setup API and templates
routes = FastAPI(title="wypt api", version="1")
routes.mount("/static", StaticFiles(directory="static"), name="static")

template = Jinja2Templates(directory="template")

api_handler = APIHandler(runtime.get_database())


@routes.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse("static/img/favicon.ico")


@routes.get("/")
def index(request: Request) -> HTMLResponse:
    """Index page."""
    return template.TemplateResponse(request, "index.html")


@routes.get("/gridsample")
def gridsample(request: Request) -> HTMLResponse:
    """Sample grid layout page."""
    return template.TemplateResponse(request, "gridsample.html")


@routes.get("/matchview")
def matchview_main(request: Request, limit: int = 100, offset: int = 0) -> HTMLResponse:
    """Main view for MatchView model."""
    previous_params, next_params = api_handler.get_matchview_params(limit, offset)
    context = {
        "previous_params": previous_params,
        "next_params": next_params,
        "matchviews": api_handler.get_matchview(limit, offset),
    }

    return template.TemplateResponse(request, "matchview/index.html", context)


@routes.get("/matchviewtable")
def matchview_table(
    request: Request,
    limit: int = 100,
    offset: int = 0,
) -> HTMLResponse:
    """Main view for MatchView model."""
    previous_params, next_params = api_handler.get_matchview_params(limit, offset)
    context = {
        "previous_params": previous_params,
        "next_params": next_params,
        "matchviews": api_handler.get_matchview(limit, offset),
    }

    return template.TemplateResponse(request, "matchview/part_table.html", context)

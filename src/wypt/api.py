from __future__ import annotations

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import _filters
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
_filters.apply_filters(template)

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
    headers = {
        "HX-Push-Url": f"/matchview?limit={limit}&offset={offset}",
    }
    context = {
        "limit": limit,
        "offset": offset,
    }

    return template.TemplateResponse(
        request=request,
        name="matchview/index.html",
        context=context,
        headers=headers,
    )


@routes.delete("/matchview/{key}")
def matchview_delete(request: Request, key: str) -> HTMLResponse:
    """Delete MatchView record."""
    if api_handler.delete_matchview(key):
        return HTMLResponse(
            status_code=204,
            headers={
                "HX-Trigger": "redrawTable",
            },
        )
    else:
        return HTMLResponse(status_code=404)


@routes.get("/matchviewtable")
def matchview_table(
    request: Request,
    limit: int = 100,
    offset: int = 0,
) -> HTMLResponse:
    """Render table partial for MatchView"""
    limit, offset = api_handler.align_pagination(limit, offset)
    previous_params, next_params = api_handler.get_matchview_params(limit, offset)
    current, total = api_handler.get_matchview_pages(limit, offset)

    headers = {
        "HX-Push-Url": f"/matchview?limit={limit}&offset={offset}",
    }
    context = {
        "limit": limit,
        "offset": offset,
        "previous_params": previous_params,
        "next_params": next_params,
        "current_page": current,
        "total_pages": total,
        "matchviews": api_handler.get_matchview(limit, offset),
    }

    return template.TemplateResponse(
        request=request,
        name="matchview/part_table.html",
        context=context,
        headers=headers,
    )

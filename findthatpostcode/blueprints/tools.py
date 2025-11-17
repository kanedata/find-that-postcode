from fastapi import APIRouter, Request

from findthatpostcode.utils import templates

bp = APIRouter(prefix="/tools")


@bp.get("/merge-geojson")
def merge_geojson(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="merge-geojson.html.j2",
        media_type="text/html",
    )


@bp.get("/reduce-geojson")
def reduce_geojson(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reduce-geojson.html.j2",
        media_type="text/html",
    )

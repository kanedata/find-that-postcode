from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.points import Point
from findthatpostcode.db import ElasticsearchDep

bp = APIRouter(prefix="/points")


@bp.get("/redirect")
def point_redirect(lat: float, lon: float, request: Request):
    return RedirectResponse(
        request.url_for(
            "get_point", latlon="{},{}.html".format(lat, lon), filetype="html"
        ),
        code=303,
    )


@bp.get("/{latlon}")
def get_point(latlon: str, es: ElasticsearchDep, request: Request):
    filetype = "json"
    if latlon.endswith(".json"):
        latlon = latlon[:-5]
    elif latlon.endswith(".html"):
        latlon = latlon[:-5]
        filetype = "html"
    lat, lon = latlon.split(",")
    result = Point.get_from_es((float(lat), float(lon)), es)
    errors = result.get_errors()
    if errors:
        return_result(result, request, filetype, "postcode.html.j2")
    if filetype == "html":
        return return_result(
            result.relationships["nearest_postcode"],
            request,
            filetype,
            "postcode.html.j2",
            point=result,
            stats=result.relationships["nearest_postcode"].get_stats(),
        )
    return return_result(result, request, filetype, "postcode.html.j2")

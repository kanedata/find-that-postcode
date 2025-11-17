from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.points import Point
from findthatpostcode.db import ElasticsearchDep

bp = APIRouter(prefix="/points")


@bp.route("/redirect")
def point_redirect(lat: float, lon: float, request: Request):
    return RedirectResponse(
        request.url_for(
            "points.get", latlon="{},{}.html".format(lat, lon), filetype="html"
        ),
        code=303,
    )


@bp.get("/{latlon}")
def get(latlon, es: ElasticsearchDep):
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
        return_result(result, filetype, "postcode.html.j2")
    if filetype == "html":
        return return_result(
            result.relationships["nearest_postcode"],
            filetype,
            "postcode.html.j2",
            point=result,
            stats=result.relationships["nearest_postcode"].get_stats(),
        )
    return return_result(result, filetype, "postcode.html.j2")

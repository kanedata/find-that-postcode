from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.points import Point
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import ElasticsearchDep

bp = APIRouter(prefix="/points")

api = APIRouter(prefix="/points")


@bp.get("/redirect")
def point_redirect(lat: float, lon: float, request: Request) -> Response:
    return RedirectResponse(
        request.url_for(
            "get_point", latlon="{},{}.html".format(lat, lon), filetype="html"
        ),
        status_code=303,
    )


@bp.get("/{latlon}")
@api.get("/{latlon}", name="legacy_get_point")
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
        return return_result(result, request, filetype, "postcode.html.j2")
    if filetype == "html":
        nearest_postcode = result.relationships.get("nearest_postcode")
        if not isinstance(nearest_postcode, Postcode):
            return return_result(result, request, filetype, "postcode.html.j2")

        return return_result(
            nearest_postcode,
            request,
            filetype,
            "postcode.html.j2",
            point=result,
            stats=nearest_postcode.get_stats(),
        )
    return return_result(result, request, filetype, "postcode.html.j2")

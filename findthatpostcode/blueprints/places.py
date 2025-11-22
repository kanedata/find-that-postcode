from http import HTTPStatus

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.places import Place
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.settings import PLACENAME_INDEX

bp = APIRouter(prefix="/places")

api = APIRouter(prefix="/places")


@bp.get("/redirect")
def point_redirect(lat: float, lon: float, request: Request) -> Response:
    return RedirectResponse(
        request.url_for("places.nearest", lat=lat, lon=lon, filetype="html"),
        status_code=HTTPStatus.SEE_OTHER,
    )


@bp.get("/nearest/{lat},{lon}")
@bp.get("/nearest/{lat},{lon}.{filetype}")
@api.get("/nearest/{lat},{lon}", include_in_schema=False)
def nearest(
    lat: float, lon: float, es: ElasticsearchDep, filetype: str = "json"
) -> Response:
    query = {
        "query": {"match_all": {}},
        "sort": [
            {"_geo_distance": {"location": {"lat": lat, "lon": lon}, "unit": "m"}}
        ],
    }

    data = es.search(
        index=PLACENAME_INDEX,
        body=query,
        ignore=[HTTPStatus.NOT_FOUND],  # type: ignore
        size=10,  # type: ignore
        _source_excludes=[],  # type: ignore
    )
    return JSONResponse(content=data)


@bp.get("/{areacode}")
@bp.get("/{areacode}.{filetype}")
@api.get("/{areacode}", name="legacy_get_place")
def get_place(
    areacode: str, es: ElasticsearchDep, request: Request, filetype: str = "json"
):
    result = Place.get_from_es(areacode, es)
    return return_result(result, request, filetype, "place.html.j2")

from fastapi import APIRouter, Request, Response

from findthatpostcode.blueprints.areas import areas_csv
from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.areas import (
    Areatype,
    area_types_count,
    get_all_areas,
)
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.utils import templates

bp = APIRouter(prefix="/areatypes")


@bp.get("/")
def all_areatypes(es: ElasticsearchDep, request: Request) -> Response:
    ats = area_types_count(es)
    return templates.TemplateResponse(
        request=request,
        name="areatypes.html.j2",
        context={"result": ats},
        media_type="text/html",
    )


@bp.get("/{areacode}")
@bp.get("/{areacode}.{filetype}")
def get_areatype(
    areacode: str,
    request: Request,
    es: ElasticsearchDep,
    filetype: str = "json",
    p: int = 1,
    size: int = 25,
):
    if filetype == "csv":
        areas = get_all_areas(es, areatypes=[areacode.strip().lower()])
        return areas_csv(areas, "{}.csv".format(areacode))
    result = Areatype.get_from_es(areacode, es)
    pagination = Pagination(page=p, size=size)
    result.get_areas(es, pagination=pagination)

    pagination.set_pagination(result.attributes["count_areas"])  # type: ignore
    nav = {
        p: request.url_for(
            "get_areatype", areacode=areacode, filetype=filetype
        ).include_query_params(**args)
        if isinstance(args, dict)
        else args
        for p, args in pagination.pagination.items()
        if args
    }
    return return_result(result, request, filetype, "areatype.html.j2", nav=nav)

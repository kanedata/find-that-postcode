from fastapi import APIRouter, Request

from findthatpostcode.blueprints.areas import areas_csv
from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.areas import (
    Areatype,
    area_types_count,
    get_all_areas,
)
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.db import get_db
from findthatpostcode.utils import templates

bp = APIRouter(prefix="/areatypes")


@bp.get("/")
def all():
    ats = area_types_count(get_db())
    return templates.TemplateResponse("areatypes.html.j2", {"result": ats})


@bp.get("/<areacode>")
@bp.get("/<areacode>.<filetype>")
def get_areatype(areacode: str, request: Request, filetype: str = "json"):
    if filetype == "csv":
        areas = get_all_areas(get_db(), areatypes=[areacode.strip().lower()])
        return areas_csv(areas, "{}.csv".format(areacode))
    result = Areatype.get_from_es(areacode, get_db())
    pagination = Pagination(request)
    result.get_areas(get_db(), pagination=pagination)

    pagination.set_pagination(result.attributes["count_areas"])
    nav = {
        p: request.url_for(
            "areatypes.get_areatype", areacode=areacode, filetype=filetype, **args
        )
        if isinstance(args, dict)
        else args
        for p, args in pagination.pagination.items()
        if args
    }
    return return_result(result, filetype, "areatype.html.j2", nav=nav)

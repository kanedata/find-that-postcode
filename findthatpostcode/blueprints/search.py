import re

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from findthatpostcode.controllers.areas import search_areas
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.utils import templates

bp = APIRouter(prefix="/search")


def is_latlon(q: str) -> dict | bool:
    r = r"^(?P<lat>\-?\d+\.[0-9]+),(?P<lon>\-?\d+\.\d+)$"
    q = q.strip().replace(" ", "")
    m = re.match(r, q)
    if m:
        return {
            "lat": m.group("lat"),
            "lon": m.group("lon"),
        }
    return False


def is_postcode(q: str) -> bool:
    r = r"^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$"
    q = q.strip().replace(" ", "").upper()
    return bool(re.match(r, q))


@bp.get("/")
def search_index(
    request: Request,
    es: ElasticsearchDep,
    q: str = "",
    p: int = 1,
    size: int = 25,
):
    if not q:
        return templates.TemplateResponse(
            request=request,
            name="areasearch.html.j2",
            context={"q": q},
            media_type="text/html",
        )

    latlon = is_latlon(q)
    if latlon:
        return RedirectResponse(
            request.url_for(
                "get_point", latlon="{},{}.html".format(latlon["lat"], latlon["lon"])
            ),
            status_code=303,
        )

    if is_postcode(q):
        return RedirectResponse(
            request.url_for("get_postcode", postcode=q, filetype="html"),
            status_code=303,
        )

    pagination = Pagination(p=p, size=size)
    areas = search_areas(
        q,
        es,
        pagination=pagination,
    )
    result = zip(areas["result"], areas["scores"])
    pagination.set_pagination(areas["result_count"])
    nav = {
        p: request.url_for("search_index").include_query_params(q=q, **args)
        if isinstance(args, dict)
        else args
        for p, args in pagination.pagination.items()
        if args
    }
    return templates.TemplateResponse(
        request=request,
        name="areasearch.html.j2",
        context={
            "result": list(result),
            "q": q,
            "total": areas["result_count"],
            "nav": nav,
        },
        media_type="text/html",
    )

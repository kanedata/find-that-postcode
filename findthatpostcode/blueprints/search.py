import re

from flask import Blueprint, redirect, render_template, request, url_for

from findthatpostcode.controllers.areas import search_areas
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.db import get_db

bp = Blueprint("search", __name__, url_prefix="/search")


def is_latlon(q):
    r = r"^(?P<lat>\-?\d+\.[0-9]+),(?P<lon>\-?\d+\.\d+)$"
    q = q.strip().replace(" ", "")
    m = re.match(r, q)
    if m:
        return {
            "lat": m.group("lat"),
            "lon": m.group("lon"),
        }
    return False


def is_postcode(q):
    r = r"^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$"
    q = q.strip().replace(" ", "").upper()
    return bool(re.match(r, q))


@bp.route("/", strict_slashes=False)
def search_index():
    q = request.values.get("q")
    if not q:
        return render_template(
            "areasearch.html.j2",
            q=q,
        )

    latlon = is_latlon(q)
    if latlon:
        return redirect(
            url_for(
                "points.get", latlon="{},{}.html".format(latlon["lat"], latlon["lon"])
            ),
            code=303,
        )

    if is_postcode(q):
        return redirect(
            url_for("postcodes.get_postcode", postcode=q, filetype="html"), code=303
        )

    pagination = Pagination(request)
    areas = search_areas(
        q,
        get_db(),
        pagination=pagination,
    )
    result = zip(areas["result"], areas["scores"])
    pagination.set_pagination(areas["result_count"])
    nav = {
        p: url_for("search.search_index", q=q, **args)
        if isinstance(args, dict)
        else args
        for p, args in pagination.pagination.items()
        if args
    }
    return render_template(
        "areasearch.html.j2",
        result=list(result),
        q=q,
        total=areas["result_count"],
        nav=nav,
    )

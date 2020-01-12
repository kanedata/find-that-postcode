import re

from flask import Blueprint, current_app, abort, jsonify, make_response, request, render_template, redirect, url_for

from .utils import return_result
from findthatpostcode.controllers.areas import Area, search_areas
from findthatpostcode.db import get_db

bp = Blueprint('search', __name__, url_prefix='/search')


def is_latlon(q):
    r = r'^(?P<lat>\-?\d+\.[0-9]+),(?P<lon>\-?\d+\.\d+)$'
    q = q.strip().replace(" ", "")
    m = re.match(r, q)
    if m:
        return {
            "lat": m.group("lat"),
            "lon": m.group("lon"),
        }
    return False

def is_postcode(q):
    r = r'^[A-Z]{1,2}[0-9][0-9A-Z]? ?[0-9][A-Z]{2}$'
    q = q.strip().replace(" ", "").upper()
    return bool(re.match(r, q))


@bp.route('/', strict_slashes=False)
def search_index():
    q = request.values.get("q")
    if not q:
        return render_template(
            'areasearch.html',
            q=q,
        )

    latlon = is_latlon(q)
    if latlon:
        return redirect(url_for('points.get', lat=latlon["lat"], lon=latlon["lon"], filetype='html'), code=303)

    if is_postcode(q):
        return redirect(url_for('postcodes.get_postcode', postcode=q, filetype='html'), code=303)

    areas = search_areas(q, get_db())
    result = zip(areas["result"], areas["scores"])
    return render_template(
        'areasearch.html',
        result=list(result),
        q=request.values.get("q"),
        total=areas['result_count']
    )

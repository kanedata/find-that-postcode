import io
import csv
import re

from flask import Blueprint, abort, jsonify, make_response, request, redirect, url_for

from .utils import return_result
from findthatpostcode.controllers.areas import Area, get_all_areas
from findthatpostcode.db import get_db

bp = Blueprint('areas', __name__, url_prefix='/areas')


@bp.route('/search')
@bp.route('/search.<filetype>')
def area_search(filetype="json"):
    return redirect(url_for('search.search_index', q=request.values.get("q")), code=301)


@bp.route('/names.csv')
def all_names():
    areas = get_all_areas(
        get_db(),
        areatypes=[a.strip().lower() for a in request.values.get("types", "").split(",") if a]
    )

    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=["code", "name", "type"])
    writer.writeheader()
    for row in areas:
        if not row.get("name") or not row.get("type"):
            continue
        if re.match(r'[A-Z][0-9]{8}', row.get("code")):
            writer.writerow(row)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=names.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_area(areacode, filetype="json"):
    result = Area.get_from_es(
        areacode,
        get_db(),
        boundary=(filetype == 'geojson'),
        examples_count=(0 if filetype == 'geojson' else 5)
    )

    if filetype == 'geojson':
        status, r = result.geoJSON()
        if status != 200:
            return abort(make_response(jsonify(message=r), status))
        return jsonify(r)

    return return_result(result, filetype, "area.html")

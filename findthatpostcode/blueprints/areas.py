import csv
import io
import re

from flask import (
    Blueprint,
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from findthatpostcode.controllers.areas import Area, get_all_areas
from findthatpostcode.db import get_db

from .utils import return_result

bp = Blueprint("areas", __name__, url_prefix="/areas")


@bp.route("/search")
@bp.route("/search.<filetype>")
def area_search(filetype="json"):
    return redirect(url_for("search.search_index", q=request.values.get("q")), code=301)


@bp.route("/names.csv")
def all_names():
    areas = get_all_areas(
        get_db(),
        areatypes=[
            a.strip().lower() for a in request.values.get("types", "").split(",") if a
        ],
    )
    return areas_csv(areas, "names.csv")


def areas_csv(areas, filename):
    si = io.StringIO()
    writer = csv.DictWriter(
        si, fieldnames=["code", "name", "type", "active", "date_start", "date_end"]
    )
    writer.writeheader()
    for row in areas:
        if not row.get("name") or not row.get("type"):
            continue
        if re.match(r"[A-Z][0-9]{8}", row.get("code")):
            writer.writerow(row)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    output.headers["Content-type"] = "text/csv"
    return output


@bp.route("/<areacodes>.geojson")
def get_area_boundary(areacodes):
    es = get_db()
    areacodes = areacodes.split("+")
    features = []
    for areacode in areacodes:
        result = Area.get_from_es(areacode, es, boundary=True, examples_count=0)
        status, r = result.geoJSON()
        if status == 200:
            features.extend(r.get("features"))
    if status != 200:
        return abort(make_response(jsonify(message=r), status))
    return jsonify({"type": "FeatureCollection", "features": features})


@bp.route("/<areacode>/children/<areatype>.geojson")
def get_area_children_boundary(areacode, areatype):
    es = get_db()
    area = Area.get_from_es(areacode, es, boundary=False, examples_count=0)
    features = []
    errors = {}
    for child_area in area.relationships["children"][areatype]:
        result = Area.get_from_es(child_area.id, es, boundary=True, examples_count=0)
        status, r = result.geoJSON()
        if status == 200:
            features.extend(r.get("features"))
        else:
            errors[child_area.id] = r
    if not features:
        return abort(make_response(jsonify(message=errors), status))
    return jsonify({"type": "FeatureCollection", "features": features})


@bp.route("/<areacode>")
@bp.route("/<areacode>.<filetype>")
def get_area(areacode, filetype="json"):
    result = Area.get_from_es(
        areacode,
        get_db(),
        boundary=(filetype == "geojson"),
        examples_count=(0 if filetype == "geojson" else 5),
    )

    if filetype == "geojson":
        status, r = result.geoJSON()
        if status != 200:
            return abort(make_response(jsonify(message=r), status))
        return jsonify(r)

    return return_result(
        result, filetype, "area.html.j2", child=request.values.get("child")
    )


@bp.route("/<areacodes>/map")
def get_area_map(areacodes):
    return render_template("area_map.html.j2", areacodes=areacodes)

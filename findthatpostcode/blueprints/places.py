import re

from flask import Blueprint, current_app, request, redirect, url_for, jsonify

from .utils import return_result
from findthatpostcode.controllers.places import Place
from findthatpostcode.db import get_db

bp = Blueprint('places', __name__, url_prefix='/places')


@bp.route('/redirect')
def point_redirect():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    return redirect(url_for('places.nearest', lat=lat, lon=lon, filetype='html'), code=303)


@bp.route('/nearest/<lat>,<lon>')
@bp.route('/nearest/<lat>,<lon>.<filetype>')
def nearest(lat, lon, filetype="json"):
    es = get_db()
    query = {
        "query": {
            "match_all": {}
        },
        "sort": [
            {
                "_geo_distance": {
                    "location": {
                        "lat": lat,
                        "lon": lon
                    },
                    "unit": "m"
                }
            }
        ]
    }

    data = es.search(
        index="geo_placename",
        body=query,
        ignore=[404],
        size=10,
        _source_excludes=[],
    )
    return jsonify(data)


@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_place(areacode, filetype="json"):
    result = Place.get_from_es(areacode, get_db())
    return return_result(result, filetype, "place.html")

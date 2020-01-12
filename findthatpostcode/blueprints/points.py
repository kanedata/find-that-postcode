import re

from flask import Blueprint, current_app, request, redirect, url_for

from .utils import return_result
from findthatpostcode.controllers.points import Point
from findthatpostcode.db import get_db

bp = Blueprint('points', __name__, url_prefix='/points')


@bp.route('/redirect')
def point_redirect():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    return redirect(url_for('points.get', latlon="{},{}.html".format(lat, lon)), code=303)


@bp.route('/<latlon>')
def get(latlon):
    filetype = 'json'
    if latlon.endswith('.json'):
        latlon = latlon[:-5]
    elif latlon.endswith('.html'):
        latlon = latlon[:-5]
        filetype = 'html'
    lat, lon = latlon.split(",")
    es = get_db()
    result = Point.get_from_es((float(lat), float(lon)), es)
    if filetype=='html':
        return return_result(result.relationships["nearest_postcode"], filetype, 'postcode.html', point=result)
    return return_result(result, filetype, 'postcode.html')

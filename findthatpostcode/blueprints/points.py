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
    return redirect(url_for('points.get', lat=lat, lon=lon, filetype='html'), code=303)


@bp.route('/<lat>,<lon>')
@bp.route('/<lat>,<lon>.<filetype>')
def get(lat, lon, filetype="json"):
    es = get_db()
    result = Point.get_from_es((float(lat), float(lon)), es)
    return return_result(result.relationships["nearest_postcode"], filetype, 'postcode.html', point=result)

from flask import Blueprint, current_app, abort, jsonify, make_response, request, render_template

from .utils import return_result
from findthatpostcode.controllers.areatypes import Areatype, area_types_count
from findthatpostcode.db import get_db

bp = Blueprint('areatypes', __name__, url_prefix='/areatypes')

@bp.route('/', strict_slashes=False)
def all():
    ats = area_types_count(get_db())
    return render_template('areatypes.html', result=ats)

@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_areatype(areacode, filetype="json"):
    result = Areatype.get_from_es(areacode, get_db())
    result.get_areas(get_db())
    return return_result(result, filetype, "areatype.html")


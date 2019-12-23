from flask import Blueprint, current_app

from .utils import return_result
from dkpostcodes.controllers.areas import Area
from dkpostcodes.db import get_db

bp = Blueprint('areas', __name__, url_prefix='/areas')

@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_area(areacode, filetype="json"):
    result = Area.get_from_es(areacode, get_db())
    return return_result(result, filetype, "area.html")

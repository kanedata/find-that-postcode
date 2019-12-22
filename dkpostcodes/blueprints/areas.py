from flask import Blueprint, current_app

from .utils import return_result
from dkpostcodes.controllers.areas import Area
from dkpostcodes.db import get_db

bp = Blueprint('areas', __name__, url_prefix='/areas')

@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_area(areacode, filetype="json"):
    # a = Area(current_app.config, get_db())
    # examples_count = 5 if filetype == "html" else 5
    # a.get_by_id(areacode.strip(), examples_count=examples_count)
    # (status, result) = a.topJSON()
    # print(result)
    # return return_result(result, status, filetype, "area.html")

    es = get_db()
    
    result = Area.get_from_es(areacode, es)
    return return_result(result, filetype, "area.html")

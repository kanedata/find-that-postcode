from flask import Blueprint, current_app, abort, jsonify, make_response, request, render_template

from .utils import return_result
from findthatpostcode.controllers.areas import Area, search_areas
from findthatpostcode.db import get_db

bp = Blueprint('areas', __name__, url_prefix='/areas')


@bp.route('/search')
@bp.route('/search.<filetype>')
def area_search(filetype="json"):
    q = request.values.get("q")
    if not q:
        return render_template(
            'areasearch.html',
            q=q,
        )


    areas = search_areas(q, get_db())
    result = zip(areas["result"], areas["scores"])
    return render_template(
        'areasearch.html',
        result=list(result),
        q=q,
        total=areas['result_count']['value']
    )

@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_area(areacode, filetype="json"):
    result = Area.get_from_es(areacode, get_db(), boundary=(filetype=='geojson'))

    if filetype == 'geojson':
        status, r = result.geoJSON()
        if status != 200:
            return abort(make_response(jsonify(message=r), status))
        return jsonify(r)

    return return_result(result, filetype, "area.html")


from flask import Blueprint, render_template, request, url_for

from .utils import return_result
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.controllers.areatypes import Areatype, area_types_count
from findthatpostcode.controllers.areas import get_all_areas
from findthatpostcode.db import get_db
from findthatpostcode.blueprints.areas import areas_csv

bp = Blueprint('areatypes', __name__, url_prefix='/areatypes')


@bp.route('/', strict_slashes=False)
def all():
    ats = area_types_count(get_db())
    return render_template('areatypes.html.j2', result=ats)


@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_areatype(areacode, filetype="json"):
    if filetype=='csv':
        areas = get_all_areas(
            get_db(),
            areatypes=[areacode.strip().lower()]
        )
        return areas_csv(areas, '{}.csv'.format(areacode))
    result = Areatype.get_from_es(areacode, get_db())
    pagination = Pagination(request)
    result.get_areas(get_db(), pagination=pagination)
    
    pagination.set_pagination(result.attributes['count_areas'])
    nav = {
        p: url_for('areatypes.get_areatype', areacode=areacode, filetype=filetype, **args) if isinstance(args, dict) else args
        for p, args in pagination.pagination.items()
        if args
    }
    return return_result(result, filetype, "areatype.html.j2", nav=nav)

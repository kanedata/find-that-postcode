import re

from flask import Blueprint, current_app

from .utils import return_result
from dkpostcodes.controllers.postcodes import Postcode
from dkpostcodes.db import get_db

bp = Blueprint('postcodes', __name__, url_prefix='/postcodes')

@bp.route('/<postcode>')
@bp.route('/<postcode>.<filetype>')
def get_postcode(postcode, filetype="json"):

    es = get_db()
    
    result = Postcode.get_from_es(postcode, es)
    return return_result(result, filetype, 'postcode.html')

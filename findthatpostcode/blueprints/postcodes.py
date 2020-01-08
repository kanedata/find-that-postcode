import re

from flask import Blueprint, current_app, request, redirect, url_for

from .utils import return_result
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import get_db

bp = Blueprint('postcodes', __name__, url_prefix='/postcodes')


@bp.route('/redirect')
def postcode_redirect():
    pcd = request.args.get("postcode")
    return redirect(url_for('postcodes.get_postcode', postcode=pcd, filetype='html'), code=303)

@bp.route('/<postcode>')
@bp.route('/<postcode>.<filetype>')
def get_postcode(postcode, filetype="json"):

    es = get_db()
    
    result = Postcode.get_from_es(postcode, es)
    return return_result(result, filetype, 'postcode.html')

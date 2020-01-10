import re

from flask import Blueprint, current_app, request, redirect, url_for, jsonify, abort, make_response
from elasticsearch.helpers import scan

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

@bp.route('/hash/<hash>')
@bp.route('/hash/<hash>.json')
def get_postcode_by_hash(hash):

    es = get_db()

    if len(hash) < 3:
        abort(400, description="Hash length must be at least 3 characters")

    fields = request.values.getlist('properties')
    name_fields = [i.replace("_name", "") for i in fields if i.endswith("_name")]

    results = scan(
        es,
        index='geo_postcode',
        query={"query": {"prefix": {"hash": hash}}},
        _source_includes=fields + name_fields,
    )
    areanames = {
        i["_id"]: i["_source"].get("name")
        for i in scan(
            es,
            index='geo_area',
            query = {"query": {"terms": {"type": name_fields}}},
            _source_includes=["name"]
        )
    }

    def get_names(data):
        return {
            i: areanames.get(data.get(i.replace("_name", "")))
            for i in fields if i.endswith("_name")
        }

    if results:
        return jsonify({
            "data": [
                {
                    "id": r["_id"],
                    **r["_source"],
                    **get_names(r["_source"])
                } for r in results
            ]
        })

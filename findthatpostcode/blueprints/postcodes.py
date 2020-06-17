from flask import Blueprint, request, redirect, url_for, jsonify, abort
from elasticsearch.helpers import scan
from dictlib import dig_get

from .utils import return_result
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import get_db
from findthatpostcode.metadata import STATS_FIELDS

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
def single_hash(hash):
    fields = request.values.getlist('properties')
    return jsonify({
        "data": get_postcode_by_hash(hash, fields)
    })


@bp.route('/hashes.json', methods = ['GET', 'POST'])
def multi_hash():
    fields = request.values.getlist('properties')
    hashes = request.values.getlist('hash')
    return jsonify({
        "data": get_postcode_by_hash(hashes, fields)
    })


def get_postcode_by_hash(hashes, fields):

    es = get_db()

    if not isinstance(hashes, list):
        hashes = [hashes]

    query = []
    for hash_ in hashes:
        if len(hash_) < 3:
            abort(400, description="Hash length must be at least 3 characters")
        query.append({
            "prefix": {
                "hash": hash_,
            },
        })

    name_fields = [i.replace("_name", "") for i in fields if i.endswith("_name")]
    extra_fields = []
    stats = [i for i in STATS_FIELDS if i[0] in fields]
    if stats:
        extra_fields.append("lsoa11")

    results = list(scan(
        es,
        index='geo_postcode',
        query={
            "query": {
                "bool": {
                    "should": query
                }
            }
        },
        _source_includes=fields + name_fields + extra_fields,
    ))
    areas = scan(
        es,
        index='geo_area',
        query={"query": {"terms": {"type": name_fields}}},
        _source_includes=["name"]
    )
    areanames = {
        i["_id"]: i["_source"].get("name") for i in areas
    }

    def get_names(data):
        return {
            i: areanames.get(data.get(i.replace("_name", "")))
            for i in fields if i.endswith("_name")
        }

    lsoas = {}

    def get_stats(data):
        lsoa = data.get("lsoa11")
        if not lsoa or not stats or lsoa not in lsoas:
            return {}
        return {
            i[0]: dig_get(lsoas[lsoa], i[3])
            for i in stats
        }

    if results:

        if stats:
            lsoas = {
                i["_id"]: i["_source"]
                for i in scan(
                    es,
                    index='geo_area',
                    query={
                        "query": {
                            "terms": {
                                "_id": [
                                    r.get("_source", {}).get("lsoa11")
                                    for r in results if r.get("_source", {}).get("lsoa11")
                                ]
                            }
                        }
                    },
                    _source_includes=[i[3] for i in stats],
                )
            }

        return [
            {
                "id": r["_id"],
                **r["_source"],
                **get_names(r["_source"]),
                **get_stats(r["_source"])
            } for r in results
        ]

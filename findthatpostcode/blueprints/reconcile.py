import json

from flask import Blueprint, current_app, request, jsonify

from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.controllers.areas import search_areas
from findthatpostcode.db import get_db
from .utils import jsonp, cors

bp = Blueprint('reconcile', __name__, url_prefix='/reconcile')


def recon_query(q, es):
    result = []
    query = q.get("query")
    if query and q.get("type") == "/postcode":
        postcode = Postcode.get_from_es(query, es)
        if postcode.found:
            result.append({
                "id": postcode.id,
                "name": postcode.id,
                "type": "/postcode",
                "score": 100,
                "match": True,
            })
    elif query:
        limit = min(int(q.get("limit", 5)), 10)
        areas = search_areas(query, es, size=limit)
        for a, score in zip(areas["result"], areas["scores"]):
            result.append({
                "id": a.id,
                "name": a.attributes["name"],
                "type": "/areas",
                "score": score,
                "match": a.attributes["name"].lower() == query.lower(),
            })
    return result


@bp.route('/', strict_slashes=False, methods=['GET', 'POST'])
@jsonp
@cors
def reconcile():

    service_spec = {
        "name": current_app.name,
        "identifierSpace": "http://rdf.freebase.com/ns/type.object.id",
        "schemaSpace": "http://rdf.freebase.com/ns/type.object.id",
        "defaultTypes": [
            {
                "id": "/postcode",
                "name": "Postcode"
            },
            {
                "id": "/area",
                "name": "Area"
            }
        ],
        "extend": {},
    }

    es = get_db()

    if "queries" in request.values:
        queries = json.loads(request.values["queries"])
        result = {}
        for slug, q in queries.items():
            result[slug] = recon_query(q, es)

        return jsonify(result)

    if "extend" in request.values:
        q = json.loads(request.values["extend"])
        properties = [p["id"] for p in q.get("properties", [])]
        ids = list(set(q.get("ids", [])))
        result = {
            "meta": [
                {"id": p for p in properties}
            ],
            "rows": {}
        }
        for i in ids:
            postcode = Postcode.get_from_es(i, es)
            result["rows"][i] = {
                p: postcode.attributes.get(p) for p in properties
            }
        return jsonify(result)

    return jsonify(service_spec)

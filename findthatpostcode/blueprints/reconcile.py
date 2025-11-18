import json
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.params import Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from findthatpostcode.controllers.areas import search_areas
from findthatpostcode.controllers.controller import Pagination
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.utils import JSONPResponse

bp = APIRouter(prefix="/reconcile")

api = APIRouter(prefix="/reconcile")


def recon_query(q, es, p: int = 1, size: int = 10):
    result = []
    query = q.get("query")
    if query and q.get("type") == "/postcode":
        postcode = Postcode.get_from_es(query, es)
        if postcode.found:
            result.append(
                {
                    "id": postcode.id,
                    "name": postcode.id,
                    "type": "/postcode",
                    "score": 100,
                    "match": True,
                }
            )
    elif query:
        pagination = Pagination(page=p, size=size)
        areas = search_areas(query, es, pagination=pagination)
        for a, score in zip(areas["result"], areas["scores"]):  # type: ignore
            result.append(
                {
                    "id": a.id,
                    "name": a.attributes["name"],
                    "type": "/areas",
                    "score": score,
                    "match": a.attributes["name"].lower() == query.lower(),
                }
            )
    return result


class ReconcileRequest(BaseModel):
    queries: dict[str, dict] | None = None
    extend: dict | None = None


@bp.get("/")
@api.get("/")
def reconcile_get(
    es: ElasticsearchDep,
    extend: Annotated[str | None, Query()] = None,
    queries: Annotated[str | None, Query()] = None,
    callback: str | None = None,
):
    return do_reconcile(es, extend, queries, callback)


@bp.post("/")
@api.post("/")
def reconcile_post(
    es: ElasticsearchDep,
    extend: Annotated[str | None, Form()] = None,
    queries: Annotated[str | None, Form()] = None,
    callback: Annotated[str | None, Query()] = None,
):
    return do_reconcile(es, extend, queries, callback)


def do_reconcile(
    es: ElasticsearchDep,
    extend: str | None = None,
    queries: str | None = None,
    callback: str | None = None,
) -> JSONResponse | JSONPResponse:
    service_spec = {
        "name": "Find that Postcode",
        "identifierSpace": "http://rdf.freebase.com/ns/type.object.id",
        "schemaSpace": "http://rdf.freebase.com/ns/type.object.id",
        "defaultTypes": [
            {"id": "/postcode", "name": "Postcode"},
            {"id": "/area", "name": "Area"},
        ],
        "extend": {},
    }

    result = service_spec

    if queries is not None:
        result = {}
        for slug, q in json.loads(queries).items():
            result[slug] = recon_query(q, es)

    elif extend is not None:
        q = json.loads(extend)
        properties = [p["id"] for p in q.get("properties", [])]
        ids = list(set(q.get("ids", [])))
        result = {"meta": [{"id": p for p in properties}], "rows": {}}
        for i in ids:
            postcode = Postcode.get_from_es(i, es)
            result["rows"][i] = {p: postcode.attributes.get(p) for p in properties}

    if callback:
        return JSONPResponse(content=result, callback=callback)
    return JSONResponse(content=result)

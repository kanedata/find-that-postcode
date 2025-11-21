from typing import Annotated

from dictlib import dig_get
from elasticsearch.helpers import scan
from fastapi import APIRouter, Form, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.metadata import (
    OAC11_CODE,
    RU11IND_CODES,
    RUC21_CODES,
    STATS_FIELDS,
)
from findthatpostcode.settings import AREA_INDEX, POSTCODE_INDEX

bp = APIRouter(prefix="/postcodes")

api = APIRouter(prefix="/postcodes")


@bp.get("/redirect")
def postcode_redirect(postcode: str, request: Request) -> Response:
    return RedirectResponse(
        request.url_for("get_postcode", postcode=postcode, filetype="html"),
        status_code=303,
    )


@bp.get("/{postcode}")
@bp.get("/{postcode}.{filetype}")
@api.get("/{postcode}", name="legacy_get_postcode")
def get_postcode(
    postcode: str, request: Request, es: ElasticsearchDep, filetype: str = "json"
):
    result = Postcode.get_from_es(postcode, es)
    return return_result(
        result, request, filetype, "postcode.html.j2", stats=result.get_stats()
    )


@bp.get("/hash/{hash_}")
@bp.get("/hash/{hash_}.json")
@api.get("/hash/{hash_}", include_in_schema=False)
def single_hash(
    hash_: str,
    properties: Annotated[list[str], Query()],
    request: Request,
    es: ElasticsearchDep,
) -> Response:
    return JSONResponse({"data": get_postcode_by_hash(es, hash_, properties)})


@bp.get("/hashes")
@bp.get("/hashes.json")
@api.get("/hashes", include_in_schema=False)
def multi_hash_get(
    hash: Annotated[str | list[str], Query()],
    properties: Annotated[list[str], Query()],
    request: Request,
    es: ElasticsearchDep,
) -> Response:
    return JSONResponse({"data": get_postcode_by_hash(es, hash, properties)})


@bp.post("/hashes")
@bp.post("/hashes.json")
@api.post("/hashes", include_in_schema=False)
def multi_hash_post(
    hash: Annotated[str | list[str], Form()],
    properties: Annotated[list[str], Form()],
    request: Request,
    es: ElasticsearchDep,
) -> Response:
    return JSONResponse({"data": get_postcode_by_hash(es, hash, properties)})


def get_postcode_by_hash(
    es: ElasticsearchDep, hashes: Annotated[str | list[str], Query()], fields: list[str]
) -> list[dict]:
    if not isinstance(hashes, list):
        hashes = [hashes]

    query = []
    for hash_ in hashes:
        if len(hash_) < 3:
            raise HTTPException(
                status_code=400, detail="Hash length must be at least 3 characters"
            )
        query.append(
            {
                "prefix": {
                    "hash": hash_,
                },
            }
        )

    name_fields = [i.replace("_name", "") for i in fields if i.endswith("_name")]
    stats_fields = []
    stats = [field for field in STATS_FIELDS if field.id in fields]
    if stats:
        for field in stats:
            if field.area not in stats_fields:
                stats_fields.append(field.area)

    results = list(
        scan(
            es,
            index=POSTCODE_INDEX,
            query={"query": {"bool": {"should": query}}},
            _source_includes=fields + name_fields + stats_fields,
        )
    )
    areas = scan(
        es,
        index=AREA_INDEX,
        query={"query": {"terms": {"type": name_fields}}},
        _source_includes=["name"],
    )
    areanames = {i["_id"]: i["_source"].get("name") for i in areas}

    def get_names(data):
        names = {}
        for i in name_fields:
            names[f"{i}_name"] = None
            if i == "oac11":
                oac_name = OAC11_CODE.get(data.get(i))
                if oac_name:
                    names[f"{i}_name"] = " > ".join(oac_name)
            elif i == "ru11ind":
                names[f"{i}_name"] = RU11IND_CODES.get(data.get(i))
            elif i == "ruc21":
                names[f"{i}_name"] = RUC21_CODES.get(data.get(i))
            else:
                names[f"{i}_name"] = areanames.get(data.get(i))
        return names

    def get_stats(data, lsoas):
        result = {}
        for field in stats:
            lsoa_code = data.get(field.area)
            if not lsoa_code or not stats or lsoa_code not in lsoas:
                continue
            result[field.id] = dig_get(lsoas[lsoa_code], field.location)
        return result

    if results:
        lsoas = {}
        if stats:
            lsoas_to_get = set()
            for r in results:
                for i in stats_fields:
                    if r.get("_source", {}).get(i):
                        lsoas_to_get.add(r.get("_source", {}).get(i))
            lsoas = {
                i["_id"]: i["_source"]
                for i in scan(
                    es,
                    index=AREA_INDEX,
                    query={"query": {"terms": {"_id": list(lsoas_to_get)}}},
                    _source_includes=[i.location for i in stats],
                )
            }

        return [
            {
                "id": r["_id"],
                **r["_source"],
                **get_names(r["_source"]),
                **get_stats(r["_source"], lsoas),
            }
            for r in results
        ]

    return []

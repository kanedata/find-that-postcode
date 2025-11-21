from elasticsearch import Elasticsearch
from fastapi import HTTPException

from findthatpostcode.crud.utils import get_or_404
from findthatpostcode.schema import Postcode
from findthatpostcode.schema.db import Postcode as PostcodeDocument
from findthatpostcode.settings import MAX_DISTANCE_FROM_POINT


def get_postcode(postcode: str, es: Elasticsearch) -> Postcode:
    postcode = postcode.replace(" ", "").upper().strip()
    postcode_end = postcode[-3:]
    postcode_start = postcode.removesuffix(postcode_end)
    postcode = f"{postcode_start} {postcode_end}"
    return get_or_404(PostcodeDocument, es, postcode).to_schema(es)


def nearest_postcodes(
    lat: float,
    lon: float,
    es: Elasticsearch,
    max_distance: int = MAX_DISTANCE_FROM_POINT,
    count: int = 5,
) -> list[Postcode]:
    if max_distance <= 0:
        raise HTTPException(
            status_code=400,
            detail="max_distance must be a positive integer",
        )
    if max_distance > MAX_DISTANCE_FROM_POINT:
        max_distance = MAX_DISTANCE_FROM_POINT
    query = {
        "query": {
            "bool": {
                "must_not": {"exists": {"field": "doterm"}},
                "filter": {
                    "geo_distance": {
                        "distance": f"{max_distance}m",
                        "location": {"lat": lat, "lon": lon},
                    }
                },
            }
        },
        "sort": [
            {"_geo_distance": {"location": {"lat": lat, "lon": lon}, "unit": "m"}}
        ],
    }
    result = (
        PostcodeDocument.search(using=es).update_from_dict(query)[0:count].execute()
    )
    if result:
        return [hit.to_schema(es) for hit in result.hits]  # type: ignore
    return []


def get_postcode_for_point(
    lat: float,
    lon: float,
    es: Elasticsearch,
    max_distance: int = MAX_DISTANCE_FROM_POINT,
) -> Postcode:
    postcodes = nearest_postcodes(lat, lon, es, max_distance, count=1)
    if not postcodes:
        raise HTTPException(
            status_code=404,
            detail=f"No postcode found within {max_distance} metres of point",
        )
    return postcodes[0]

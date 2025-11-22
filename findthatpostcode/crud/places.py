from http import HTTPStatus

from elasticsearch import Elasticsearch
from fastapi import HTTPException

from findthatpostcode.crud.postcode import nearest_postcodes
from findthatpostcode.crud.utils import get_or_404
from findthatpostcode.schema import Place, Postcode
from findthatpostcode.schema.db import Place as PlaceDocument
from findthatpostcode.settings import MAX_DISTANCE_FROM_POINT


def get_place(placecode: str, es: Elasticsearch) -> Place:
    return get_or_404(PlaceDocument, es, placecode).to_schema()


def get_postcodes_for_place(
    place: Place, es: Elasticsearch, within: int = MAX_DISTANCE_FROM_POINT
) -> list[Postcode]:
    if not place.location:
        return []
    if not place.location.lat or not place.location.lon:
        return []
    return nearest_postcodes(
        place.location.lat, place.location.lon, es, max_distance=within
    )


def get_nearby_places(
    lat: float,
    lon: float,
    es: Elasticsearch,
    max_distance: int = MAX_DISTANCE_FROM_POINT,
    count: int = 5,
) -> list[Place]:
    if max_distance <= 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
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
    result = PlaceDocument.search(using=es).update_from_dict(query)[0:count].execute()
    if result:
        return [hit.to_schema() for hit in result.hits]  # type: ignore
    return []


def get_places_for_record(
    record: Place | Postcode, es: Elasticsearch, within: int = MAX_DISTANCE_FROM_POINT
) -> list[Place]:
    if not record.location:
        return []
    if not record.location.lat or not record.location.lon:
        return []
    return get_nearby_places(
        record.location.lat, record.location.lon, es, max_distance=within
    )

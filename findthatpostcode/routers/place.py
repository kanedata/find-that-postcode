from fastapi import APIRouter

from findthatpostcode.crud.places import (
    get_place,
    get_places_for_record,
    get_postcodes_for_place,
)
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.schema import Place as PlaceResponse
from findthatpostcode.schema import Postcode as PostcodeResponse

router = APIRouter(tags=["Place"])


@router.get("/{placecode}/places", response_model_exclude_unset=True)
async def read_nearby_places(
    placecode: str, es: ElasticsearchDep
) -> list[PlaceResponse]:
    place = get_place(placecode, es)
    return get_places_for_record(place, es)


@router.get("/{placecode}/postcodes", response_model_exclude_unset=True)
async def read_nearby_postcodes(
    placecode: str, es: ElasticsearchDep, within: int = 1000
) -> list[PostcodeResponse]:
    place = get_place(placecode, es)
    return get_postcodes_for_place(place, es, within=within)


@router.get("/{placecode}", response_model_exclude_unset=True)
async def read_place(placecode: str, es: ElasticsearchDep) -> PlaceResponse:
    return get_place(placecode, es)

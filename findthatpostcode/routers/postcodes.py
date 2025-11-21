from fastapi import APIRouter

from findthatpostcode.crud.places import get_places_for_record
from findthatpostcode.crud.postcode import get_postcode, get_postcode_for_point
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.schema import Place as PlaceResponse
from findthatpostcode.schema import Postcode as PostcodeResponse

router = APIRouter(tags=["Postcode"])


@router.get("/nearest/{lat},{lon}", response_model_exclude_unset=True, tags=["Point"])
async def nearest_to_point(
    lat: float, lon: float, es: ElasticsearchDep
) -> PostcodeResponse:
    return get_postcode_for_point(lat, lon, es)  # type: ignore


@router.get("/{postcode}", response_model_exclude_unset=True)
async def read_postcode(postcode: str, es: ElasticsearchDep) -> PostcodeResponse:
    return get_postcode(postcode, es)  # type: ignore


@router.get("/{postcode}/places", response_model_exclude_unset=True)
async def read_nearby_places(
    postcode: str, es: ElasticsearchDep
) -> list[PlaceResponse]:
    postcode_obj = get_postcode(postcode, es)
    return get_places_for_record(postcode_obj, es)

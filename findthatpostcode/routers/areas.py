from fastapi import APIRouter

from findthatpostcode.areatypes import AreaTypeEnum
from findthatpostcode.crud.areas import (
    get_area,
    get_area_boundary,
    get_areas,
    get_child_areas,
    get_example_postcodes,
)
from findthatpostcode.db import ElasticsearchDep, S3Dep
from findthatpostcode.schema import Area as AreaResponse
from findthatpostcode.schema import AreaGeoJSON, AreaGeoJSONFeature
from findthatpostcode.schema import Postcode as PostcodeResponse
from findthatpostcode.utils import GeoJSONResponse

router = APIRouter(tags=["Area"])


@router.get(
    "/{areacodes}.geojson",
    response_class=GeoJSONResponse,
    response_model_exclude_unset=True,
    tags=["GeoJSON"],
)
async def read_area_geojson(
    areacodes: str, es: ElasticsearchDep, s3_client: S3Dep
) -> AreaGeoJSON:
    areacode_list: list[str] = areacodes.split("+")
    features = []
    areas = list(get_areas(areacode_list, es))
    for area in areas:
        features.append(
            AreaGeoJSONFeature(
                properties=area, geometry=get_area_boundary(area, s3_client)
            )
        )
    return AreaGeoJSON(features=features)


@router.get("/{areacode}/example_postcodes", response_model_exclude_unset=True)
async def read_example_postcodes(
    areacode: str, es: ElasticsearchDep
) -> list[PostcodeResponse]:
    area = get_area(areacode, es)
    return get_example_postcodes(area, es)


@router.get(
    "/{areacode}/children/{areatype}.geojson",
    response_class=GeoJSONResponse,
    response_model_exclude_unset=True,
    tags=["GeoJSON"],
)
async def read_area_children_geojson(
    areacode: str, areatype: AreaTypeEnum, es: ElasticsearchDep, s3_client: S3Dep
) -> AreaGeoJSON:
    area = get_area(areacode, es)
    areas = get_child_areas(area, areatype, es)
    features = []
    for area in areas:
        features.append(
            AreaGeoJSONFeature(
                properties=area, geometry=get_area_boundary(area, s3_client)
            )
        )
    return AreaGeoJSON(features=features)


@router.get("/{areacode}/children/{areatype}", response_model_exclude_unset=True)
async def read_area_children(
    areacode: str, areatype: AreaTypeEnum, es: ElasticsearchDep
) -> list[AreaResponse]:
    area = get_area(areacode, es)
    return get_child_areas(area, areatype, es)


@router.get("/{areacode}", response_model_exclude_unset=True)
async def read_area(areacode: str, es: ElasticsearchDep) -> AreaResponse:
    return get_area(areacode, es)

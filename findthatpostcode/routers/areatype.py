from fastapi import APIRouter

from findthatpostcode.areatypes import AreaTypeEnum
from findthatpostcode.crud.areatype import get_areas_for_areatype, get_areatype
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.schema import AreaBase
from findthatpostcode.schema import AreaType as AreaTypeResponse

router = APIRouter(tags=["Area Type"])


@router.get("/{areatype}", response_model_exclude_unset=True)
async def read_areatype(
    es: ElasticsearchDep, areatype: AreaTypeEnum
) -> AreaTypeResponse:
    return get_areatype(areatype, es)  # type: ignore


@router.get("/{areatype}/areas", response_model_exclude_unset=True)
async def read_areatype_areas(
    es: ElasticsearchDep, areatype: AreaTypeEnum
) -> list[AreaBase]:
    areatype_obj = get_areatype(areatype, es)
    return get_areas_for_areatype(areatype_obj, es)

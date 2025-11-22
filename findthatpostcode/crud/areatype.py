from http import HTTPStatus

from elasticsearch import Elasticsearch
from fastapi import HTTPException

from findthatpostcode.areatypes import AREA_TYPES, AreaTypeEnum
from findthatpostcode.schema import AreaBase, AreaType
from findthatpostcode.schema.db import Area as AreaDocument


def get_areatype(areatype: AreaTypeEnum, es: Elasticsearch) -> AreaType:
    areatype_obj = AREA_TYPES.get(areatype)
    if not areatype_obj:
        for areatype_key, area in AREA_TYPES.items():
            if areatype in area["entities"]:
                areatype_obj = area
                break
    if not areatype_obj:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"AreaType {areatype} not found"
        )
    return AreaType(**areatype_obj, id=areatype)


def get_areas_for_areatype(
    areatype: AreaType, es: Elasticsearch, page: int = 1, size: int = 100
) -> list[AreaBase]:
    query = {
        # "query": {"match": {"type": areatype.id}},
        "query": {
            "bool": {
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {"terms": {"type": [areatype.id]}},
                                {"terms": {"entity": areatype.entities}},
                            ]
                        }
                    }
                ],
            }
        }
    }
    start_index = (page - 1) * size
    end_index = page * size
    result = (
        AreaDocument.search(using=es)
        .update_from_dict(query)[start_index:end_index]
        .execute()
    )

    if result:
        return [hit.to_base_schema() for hit in result.hits]  # type: ignore
    return []

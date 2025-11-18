from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, model_validator

from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.db import ElasticsearchDep

router = APIRouter()


class Location(BaseModel):
    lat: float | None = None
    lon: float | None = None


class OAC11(BaseModel):
    code: str | None = None
    group: str | None = None
    subgroup: str | None = None
    supergroup: str | None = None


class RUC21(BaseModel):
    code: str | None = None
    description: str | None = None


class Area(BaseModel):
    id: str | None = None
    name: str | None = None


class PostcodeAreas(BaseModel):
    bua24: Area | None = None
    ced: Area | None = None
    ctry: Area | None = None
    cty: Area | None = None
    icb: Area | None = None
    itl: Area | None = None
    lad: Area | None = None
    laua: Area | None = None
    lep1: Area | None = None
    lep2: Area | None = None
    lsoa11: Area | None = None
    lsoa21: Area | None = None
    msoa11: Area | None = None
    msoa21: Area | None = None
    nhser: Area | None = None
    oa11: Area | None = None
    oa21: Area | None = None
    park: Area | None = None
    pcon: Area | None = None
    pfa: Area | None = None
    rgn: Area | None = None
    sicbl: Area | None = None
    ttwa: Area | None = None
    ward: Area | None = None
    wd: Area | None = None
    wz11: Area | None = None


class IMD(BaseModel):
    year: int | None = None
    rank: int | None = None
    decile: int | None = None
    total: int | None = None


class PostcodeStats(BaseModel):
    imd: list[IMD] | None = None
    oac11: OAC11 | None = None
    ruc21: RUC21 | None = None


class PostcodeResponse(BaseModel):
    dointr: datetime | None = None
    doterm: datetime | None = None
    imd: int | None = None
    location: Location | None = None
    oseast1m: int | None = None
    osgrdind: int | None = None
    osnrth1m: int | None = None
    pcd: str | None = None
    pcd2: str | None = None
    pcd7: str | None = None
    pcd8: str | None = None
    pcds: str | None = None
    usertype: int | None = None
    areas: PostcodeAreas | None = None
    stats: PostcodeStats | None = None

    @model_validator(mode="before")
    @classmethod
    def update_from_attributes(cls, data: Postcode) -> Any:
        result = data.attributes.copy()

        areas = {}
        for area_field in PostcodeAreas.model_fields.keys():
            area_code = data.attributes.get(area_field)
            area_data = {"id": area_code}
            if area_code:
                name_key = f"{area_field}_name"
                if data.attributes.get(name_key):
                    area_data["name"] = data.attributes.pop(name_key)
            areas[area_field] = area_data
        result["areas"] = areas

        stats = {}
        for stats_field in PostcodeStats.model_fields.keys():
            if stats_field == "imd":
                imd_data = defaultdict(dict)
                for key, value in data.get_stats().items():
                    year, value_key = key.removeprefix("imd").split("_")
                    imd_data[year]["year"] = int(year)
                    imd_data[year][value_key] = value
                stats["imd"] = imd_data.values()
            else:
                stats[stats_field] = data.attributes.pop(stats_field, None)
        result["stats"] = stats

        return result


@router.get("/{postcode}", tags=["postcodes"])
async def read_postcode(postcode: str, es: ElasticsearchDep) -> PostcodeResponse:
    return Postcode.get_from_es(postcode, es)  # type: ignore

import enum
from collections import defaultdict
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, model_validator

from findthatpostcode.controllers.areas import Area as AreaController
from findthatpostcode.controllers.postcodes import Postcode as PostcodeController
from findthatpostcode.schema.geojson import Feature, FeatureCollection


class Location(BaseModel):
    lat: float | None = None
    lon: float | None = None
    osgrdind: int | None = None
    oseast1m: int | None = None
    osnrth1m: int | None = None


class ClassificationType(enum.StrEnum):
    OAC = "OAC"
    RURAL_URBAN = "Rural/Urban"
    IMD = "IMD"


class Classification(BaseModel):
    type: ClassificationType
    year: int | None = None
    code: str | None = None
    description: str | None = None
    subgroup: str | None = None
    supergroup: str | None = None


class AreaEquivalents(BaseModel):
    mhclg: str | None = None
    nhs: str | None = None
    ons: str | None = None
    scottish_government: str | None = None
    welsh_government: str | None = None


class StatutoryInstrument(BaseModel):
    id: str | None = None
    title: str | None = None


class AreaBase(BaseModel):
    code: str | None = None
    name: str | None = None

    @model_validator(mode="before")
    @classmethod
    def update_from_attributes(cls, data: "AreaController | dict") -> Any:
        if isinstance(data, dict):
            return data
        return data.attributes.copy()


class Area(AreaBase):
    active: bool = True
    alternative_names: list[str] = []
    areachect: float | None = None
    areaehect: float | None = None
    areaihect: float | None = None
    arealhect: float | None = None
    date_end: datetime | None = None
    date_start: datetime | None = None
    entity: str | None = None
    equivalents: AreaEquivalents | None = None
    name_welsh: str | None = None
    owner: str | None = None
    statutory_instrument: StatutoryInstrument | None = None

    parent: AreaBase | None = None
    predecessor: list[AreaBase] = []
    successor: list[AreaBase] = []
    ctry: AreaBase | None = None

    type: str | None = None

    child_count: int | None = None
    child_counts: dict[str, int] | None = None

    # "areatype": 0,
    # "child_count": 0,
    # "child_counts": {},
    # "ctry": "E92000001",
    # "ctry_name": "England"
    @model_validator(mode="before")
    @classmethod
    def update_from_attributes(cls, data: "AreaController | dict") -> Any:
        if isinstance(data, dict):
            return data
        result = data.attributes.copy()

        if result.get("ctry"):
            ctry_data = {
                "code": result.get("ctry"),
                "name": result.get("ctry_name"),
            }
            result["ctry"] = ctry_data

        if result.get("statutory_instrument_id") or result.get(
            "statutory_instrument_title"
        ):
            si_data = {
                "id": result.get("statutory_instrument_id"),
                "title": result.get("statutory_instrument_title"),
            }
            result["statutory_instrument"] = si_data

        if result.get("parent"):
            parent_data = {
                "code": result.get("parent"),
                "name": result.get("parent_name"),
            }
            result["parent"] = parent_data

        if result.get("predecessor"):
            predecessors = []
            for predecessor_code in result["predecessor"]:  # type: ignore
                predecessors.append(
                    {
                        "code": predecessor_code,
                    }
                )
            result["predecessor"] = predecessors

        if result.get("successor"):
            successors = []
            for successor_code in result["successor"]:  # type: ignore
                successors.append(
                    {
                        "code": successor_code,
                    }
                )
            result["successor"] = successors

        return result


class AreaGeoJSONFeature(Feature):
    properties: Area | None = None  # type: ignore


class AreaGeoJSON(FeatureCollection):
    features: list[AreaGeoJSONFeature] | None = None  # type: ignore


class PostcodeAreas(BaseModel):
    bua22: AreaBase | None = None
    bua24: AreaBase | None = None
    ced: AreaBase | None = None
    ctry: AreaBase | None = None
    cty: AreaBase | None = None
    eer: AreaBase | None = None
    hlth: AreaBase | None = None
    icb: AreaBase | None = None
    itl: AreaBase | None = None
    lad: AreaBase | None = None
    laua: AreaBase | None = None
    lep1: AreaBase | None = None
    lep2: AreaBase | None = None
    lsoa11: AreaBase | None = None
    lsoa21: AreaBase | None = None
    msoa11: AreaBase | None = None
    msoa21: AreaBase | None = None
    nhser: AreaBase | None = None
    oa11: AreaBase | None = None
    oa21: AreaBase | None = None
    parish: AreaBase | None = None
    park: AreaBase | None = None
    pcon: AreaBase | None = None
    pfa: AreaBase | None = None
    rgd: AreaBase | None = None
    rgn: AreaBase | None = None
    sicbl: AreaBase | None = None
    ttwa: AreaBase | None = None
    ward: AreaBase | None = None
    wd: AreaBase | None = None
    wz11: AreaBase | None = None


class IMD(BaseModel):
    type: Literal[ClassificationType.IMD] = ClassificationType.IMD
    year: int
    rank: int | None = None
    decile: int | None = None
    total: int | None = None


class PostcodeStats(BaseModel):
    imd: list[IMD] | None = None
    classification: list[Classification] | None = None


class Postcode(BaseModel):
    dointr: date | None = None
    doterm: date | None = None
    location: Location | None = None
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
    def update_from_attributes(cls, data: PostcodeController | dict) -> Any:
        stats_from_controller = {}
        if isinstance(data, PostcodeController):
            stats_from_controller = data.get_stats()
            data = data.attributes.copy()

        for field in ["osgrdind", "oseast1m", "osnrth1m"]:
            if data.get(field):
                data["location"] = data.get("location", {})
                if isinstance(data["location"], dict):
                    data["location"][field] = data.pop(field)
                elif hasattr(data["location"], field):
                    setattr(
                        data["location"],
                        field,
                        data.pop(field),
                    )

        if not data.get("areas"):
            areas = {}
            for area_field in PostcodeAreas.model_fields.keys():
                area_code = data.get(area_field)
                area_data = {"code": area_code, "name": None}
                if area_code:
                    name_key = f"{area_field}_name"
                    if data.get(name_key):
                        area_data["name"] = data.pop(name_key)
                areas[area_field] = area_data
            data["areas"] = areas

        if not data.get("stats"):
            stats = {}
            for stats_field in PostcodeStats.model_fields.keys():
                if stats_field == "imd":
                    imd_data = defaultdict(dict)
                    for key, value in stats_from_controller.items():
                        year, value_key = key.removeprefix("imd").split("_")
                        imd_data[year]["year"] = int(year)
                        imd_data[year][value_key] = value
                    stats["imd"] = imd_data.values()
                elif stats_field == "classification":
                    classifications = []
                    for field, type_, year in [
                        ("oac11", ClassificationType.OAC, 2011),
                        ("ru11ind", ClassificationType.RURAL_URBAN, 2011),
                        ("ruc21", ClassificationType.RURAL_URBAN, 2021),
                    ]:
                        class_code = data.get(field)
                        if isinstance(class_code, dict):
                            class_code["type"] = type_
                            class_code["year"] = year
                            if class_code.get("group") and not class_code.get(
                                "description"
                            ):
                                class_code["description"] = class_code.pop("group")
                            classifications.append(class_code)
                    stats["classification"] = classifications
            data["stats"] = stats

        return data


class AreaType(BaseModel):
    id: str | None = None
    name: str | None = None
    entities: list[str] | None = None
    theme: str | None = None
    full_name: str | None = None
    description: str | None = None
    countries: list[str] | None = None
    count_areas: int | None = None


class PlaceBase(BaseModel):
    code: str | None = None
    name: str | None = None


class Place(PlaceBase):
    location: Location | None = None
    areas: PostcodeAreas | None = None
    type: str | None = None
    country: str | None = None

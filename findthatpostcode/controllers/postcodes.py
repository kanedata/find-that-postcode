import re
from datetime import datetime
from http import HTTPStatus

from dictlib import dig_get
from elasticsearch import Elasticsearch

from findthatpostcode.controllers.areas import Area
from findthatpostcode.controllers.controller import Controller
from findthatpostcode.controllers.places import Place
from findthatpostcode.metadata import (
    OAC11_CODE,
    OTHER_CODES,
    RU11IND_CODES,
    RUC21_CODES,
    STATS_FIELDS,
)
from findthatpostcode.settings import PLACENAME_INDEX, POSTCODE_INDEX
from findthatpostcode.utils import ESConfig, clean_postcode


class Postcode(Controller):
    es_index = POSTCODE_INDEX
    url_slug = "postcodes"
    date_fields = ["dointr", "doterm"]
    not_area_fields = ["osgrdind", "usertype"]

    def __init__(
        self,
        id: str,
        data: dict | None = None,
        pcareas: list[Area] | None = None,
        places: list[Place] | None = None,
    ):
        super().__init__(id, data)
        if pcareas:
            self.relationships["areas"] = pcareas
            self.relationships["nearest_places"] = places

    def __repr__(self: "Postcode") -> str:
        return "<Postcode {}>".format(self.id)

    @classmethod
    def get_from_es(
        cls: type["Postcode"],
        id: str,
        es: Elasticsearch,
        es_config: ESConfig | None = None,
    ):
        if not es_config:
            es_config = ESConfig(es_index=cls.es_index, es_type=cls.es_type)
        data = es.get(
            index=es_config.es_index,
            doc_type=es_config.es_type,
            id=cls.parse_id(id),
            ignore=[HTTPStatus.NOT_FOUND],  # type: ignore
            _source_excludes=es_config._source_exclude,  # type: ignore
        )

        if not data.get("found"):
            return cls(id)

        pcareas = []
        postcode = data.get("_source")
        for k in list(postcode.keys()):
            if isinstance(postcode[k], str) and re.match(r"[A-Z][0-9]{8}", postcode[k]):
                area = Area.get_from_es(postcode[k], es, examples_count=0)
                if area.found:
                    postcode[k + "_name"] = area.attributes.get("name")
                    pcareas.append(area)

        places = cls.get_nearest_places(data.get("_source", {}).get("location"), es, 10)
        return cls(data.get("_id"), data.get("_source"), pcareas, places)

    def process_attributes(self, data: dict) -> dict:
        # turn dates into dates
        for i in self.date_fields:
            if data.get(i) and not isinstance(data[i], datetime):
                try:
                    data[i] = datetime.strptime(data[i][0:10], "%Y-%m-%d")
                except ValueError:
                    continue

        oac11 = data.get("oac11")
        if isinstance(oac11, str):
            oac11_data = OAC11_CODE.get(oac11)
            if oac11_data:
                data["oac11"] = {
                    "code": oac11,
                    "supergroup": oac11_data[0],
                    "group": oac11_data[1],
                    "subgroup": oac11_data[2],
                }

        ru11ind = data.get("ru11ind")
        if isinstance(ru11ind, str) and RU11IND_CODES.get(ru11ind):
            data["ru11ind"] = {
                "code": ru11ind,
                "description": RU11IND_CODES.get(ru11ind),
            }

        ruc21 = data.get("ruc21")
        if isinstance(ruc21, str) and RUC21_CODES.get(ruc21):
            data["ruc21"] = {
                "code": ruc21,
                "description": RUC21_CODES.get(ruc21),
            }

        return data

    @staticmethod
    def get_nearest_places(
        location: dict[str, float], es: Elasticsearch, examples_count: int = 10
    ):
        if not location:
            return []
        query = {
            "query": {"match": {"descnm": {"query": "LOC"}}},
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": location.get("lat"),
                            "lon": location.get("lon"),
                        },
                        "unit": "m",
                    }
                }
            ],
        }
        example = es.search(
            index=PLACENAME_INDEX,
            body=query,
            size=examples_count,  # type: ignore
        )
        return [Place(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    def get_attribute(self, attr: str) -> str | dict | None:
        """
        Get an attribute or area by the field name

        Adding "_name" to end of the code will return the name rather than code
        """
        if attr in self.attributes:
            return self.attributes.get(attr)  # type: ignore

        for a in self.relationships["areas"]:  # type: ignore
            if attr.endswith("_name"):
                if a.relationships["areatype"].id == attr[:-5]:
                    return a.attributes.get("name")
            else:
                if a.relationships["areatype"].id == attr:
                    return a.id

    def get_area(self, areatype: str) -> "Area | None":
        """
        Get the area for this postcode based on the type
        """
        area_id = self.attributes.get(areatype)
        if area_id:
            for a in self.relationships["areas"]:  # type: ignore
                if a.id == area_id:
                    return a

        for a in self.relationships["areas"]:  # type: ignore
            if a.relationships["areatype"].id == areatype:
                return a

    @staticmethod
    def parse_id(id: str | tuple[float, float] | None) -> str:
        """
        standardises a postcode into the correct format
        """
        if not isinstance(id, str):
            return ""
        return clean_postcode(id)

    def toJSON(self, role: str = "top") -> tuple[dict, list]:  # type: ignore
        json, included = super().toJSON(role)
        for i in self.date_fields:
            if json.get("attributes", {}).get(i) and isinstance(
                json["attributes"][i], datetime
            ):
                json["attributes"][i] = json["attributes"][i].strftime("%Y-%m-%d")

        return json, included

    def get_stats(self) -> dict[str, int | None]:
        stats_block = {}
        for field in STATS_FIELDS:
            field_type = field.id.removesuffix("_rank").removesuffix("_decile")
            if self.attributes.get("ctry") is not None:
                stats_block[f"{field_type}_total"] = OTHER_CODES.get("imd", {}).get(
                    f"{self.attributes['ctry']}-{field_type}"
                )
            if self.found and field.area in self.attributes:
                lsoa_code = self.attributes.get(field.area)
                for area in self.relationships.get("areas", []):  # type: ignore
                    if area.id == lsoa_code:
                        stats_block[field.id] = dig_get(area.attributes, field.location)
                        break
        return stats_block

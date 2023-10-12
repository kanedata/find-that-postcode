from findthatpostcode.controllers.controller import Controller

from ..metadata import AREA_TYPES
from . import areas


class Areatype(Controller):
    es_index = "geo_entity"
    url_slug = "areatypes"
    areatypes = AREA_TYPES

    def __init__(self, id, data=None):
        if not data:
            data = self.areatypes.get(id)
        super().__init__(id, data)

    def __repr__(self):
        return "<AreaType {}>".format(self.id)

    def process_attributes(self, data):
        if isinstance(data, (list, tuple)):
            return {
                "code": data[0],
                "entities": data[1],
                "name": data[2],
                "full_name": data[3],
                "description": data[4],
                "abbreviation": data[0],
            }
        return data

    def get_name(self, country=None):
        if isinstance(country, str):
            country = country[0].upper()
        if self.id.startswith("lsoa") and country == "S":
            return "Data Zone"
        if self.id.startswith("lsoa") and country == "N":
            return "Super Output Area"
        if self.id.startswith("msoa") and country == "S":
            return "Intermediate Zone"

        return self.attributes.get("name")

    @classmethod
    def get_from_es(cls, id, es, es_config=None, full=False):
        if cls.areatypes.get(id):
            return cls(id)
        return super().get_from_es(id, es, es_config=es_config)

    def get_areas(self, es, es_config=None, pagination=None):
        query = {
            "query": {
                "function_score": {
                    "query": {"match": {"type": self.id}},
                    "random_score": {},
                }
            }
        }
        search_params = dict(
            index="geo_area",
            body=query,
            sort="_id:asc",
        )
        if pagination:
            search_params["from_"] = pagination.from_
            search_params["size"] = pagination.size
        example = es.search(**search_params)
        self.relationships["areas"] = [
            areas.Area(e["_id"], e["_source"]) for e in example["hits"]["hits"]
        ]
        self.attributes["count_areas"] = self.get_total_from_es(example)


def area_types_count(es, es_config=None):
    if not es_config:
        es_config = {}

    # fetch counts per entity
    query = {
        "size": 0,
        "aggs": {"group_by_type": {"terms": {"field": "type.keyword", "size": 100}}},
    }
    result = es.search(
        index=es_config.get("es_index", areas.Area.es_index),
        body=query,
        ignore=[404],
        _source_includes=[],
    )
    return {
        i["key"]: i["doc_count"]
        for i in result.get("aggregations", {})
        .get("group_by_type", {})
        .get("buckets", [])
    }

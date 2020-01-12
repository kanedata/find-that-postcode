from ..metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import *
from . import areas


class Areatype(Controller):

    es_index = 'geo_entity'
    url_slug = 'areatypes'
    areatypes = {i[0]: i for i in AREA_TYPES}

    def __init__(self, id, data=None):
        if not data:
            data = self.areatypes.get(id)
        super().__init__(id, data)

    def __repr__(self):
        return '<AreaType {}>'.format(self.id)

    def process_attributes(self, data):
        if isinstance(data, (list, tuple)):
            return {
                "code": data[0],
                "related_codes": data[1],
                "name": data[2],
                "full_name": data[3],
                "description": data[4],
                "abbreviation": data[0],
            }
        return data

    @classmethod
    def get_from_es(cls, id, es, es_config=None, full=False):
        if cls.areatypes.get(id):
            return cls(id)
        return super().get_from_es(id, es, es_config=es_config)

    def get_areas(self, es, es_config=None, examples_count=10):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "match": {
                            "type": self.id
                        }
                    },
                    "random_score": {}
                }
            }
        }
        example = es.search(index='geo_area', body=query, size=examples_count)
        self.relationships["areas"] = [areas.Area(e["_id"], e["_source"]) for e in example["hits"]["hits"]]
        self.attributes["count_areas"] = self.get_total_from_es(example)

def area_types_count(es, es_config=None):
    if not es_config:
        es_config = {}

    # fetch counts per entity
    query = {
        "size": 0,
        "aggs": {
            "group_by_type": {
                "terms": {
                    "field": "type.keyword",
                    "size": 100
                }
            }
        }
    }
    result = es.search(
        index=es_config.get("es_index", areas.Area.es_index),
        body=query,
        ignore=[404],
        _source_includes=[],
    )
    return {
        i["key"]: i["doc_count"]
        for i in result["aggregations"]["group_by_type"]["buckets"]
    }

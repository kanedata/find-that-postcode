from ..metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import *
from . import areas


class Areatype(Controller):

    es_index = 'geo_entity'
    url_slug = 'areatypes'
    

    def __init__(self, id, data=None):
        super().__init__(id, data)
        self.areatypes = {i[0]: i for i in AREA_TYPES}

    def __repr__(self):
        return '<AreaType {}>'.format(self.id)

    def get_by_id(self, areatype, p=1, size=None):
        self.set_from_data(areatype)
        self.areas = []
        if self.es and not self.config.get("stop_recursion"):
            self.relationships["areas"] = []
            self.pagination = Pagination()
            version = self.get_es_version(self.es)[0]
            sorting = "name.keyword:asc" if version >= 5 else "name:asc"

            query = {
                "query": {
                    "match": {
                        "entity": self.id
                    }
                }
            }
            result = self.es.search(
                index=self.config.get("es_index"), 
                body=query, 
                from_=self.pagination.from_, 
                size=self.pagination.size, 
                _source_excludes=["boundary"],
                sort=sorting
            )
            if result["hits"]["total"] > 0:
                self.config["stop_recursion"] = True
                self.relationships["areas"] = [controllers.areas.Area(self.config).set_from_data(a) for a in result["hits"]["hits"]]
                self.attributes["count_areas"] = result["hits"]["total"]
                self.pagination.set_pagination(self.attributes["count_areas"])
            else:
                self.found = False
        return self

    def set_from_data(self, areatype):
        self.found = True
        self.id = areatype
        self.attributes = {
            "id": areatype,
            "count_areas": None,
            "name": areatype,
            "full_name": areatype,
            "description": ""
        }
        typedata = self.areatypes.get(areatype)
        if typedata:
            self.attributes["name"] = typedata[1]
            self.attributes["full_name"] = typedata[2]
            self.attributes["description"] = typedata[3]

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


class Areatypes(Controller):

    url_slug = 'areatypes'

    def __init__(self, id="__all", data=None):
        super().__init__(id, data)
        self.areatypes = {i[0]: i for i in AREA_TYPES}

    def __repr__(self):
        return '<AreaTypes>'

    @classmethod
    def get_from_es(cls, es, es_config=None, examples_count=5, boundary=False):
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
            _source_excludes=["boundary"],
        )
        doc_counts = {i["key"]: i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}
        for e in entities:
            e.doc_count = doc_counts.get(e.id)
        return cls(data=entities)

    def topJSON(self):
        return (200, {
            "data": [a.toJSON()[1] for a in self.attributes],
            "links": {"self": "/areatypes"}
        })

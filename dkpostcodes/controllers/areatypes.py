from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import *
from . import areas


class Areatype(Controller):

    es_type = 'code'
    url_slug = 'areatypes'

    def __init__(self, config):
        self.areatypes = {i[0]: i for i in AREA_TYPES}
        super().__init__(config)

    def get_by_id(self, areatype, p=1, size=None):
        self.set_from_data(areatype)
        self.areas = []
        if self.config.get("es") and not self.config.get("stop_recursion"):
            self.relationships["areas"] = []
            self.pagination = Pagination()
            version = self.get_es_version(self.config.get("es"))[0]
            sorting = "name.keyword:asc" if version >= 5 else "name:asc"

            query = {
                "query": {
                    "match": {
                        "type": self.id
                    }
                }
            }
            result = self.config.get("es").search(
                index=self.config.get("es_index"), 
                doc_type=self.es_type, 
                body=query, 
                from_=self.pagination.from_, 
                size=self.pagination.size, 
                _source_exclude=["boundary"],
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


class Areatypes(Controller):

    es_type = 'code'
    url_slug = 'areatypes'

    def __init__(self, config):
        super().__init__(config)

    def get(self):
        self.areatypes = {i[0]: i for i in AREA_TYPES}
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
        result = self.config.get("es").search(index=self.config.get("es_index", "postcode"), doc_type=self.es_type, body=query, _source_exclude=["boundary"])
        self.area_counts = {i["key"]: i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}
        self.attributes = []
        for a in self.areatypes:
            areatype = Areatype(self.config)
            areatype.set_from_data(a)
            if a in self.area_counts:
                areatype.attributes["count_areas"] = self.area_counts[a]
            self.attributes.append(areatype)

    def topJSON(self):
        return (200, {
            "data": [a.toJSON()[1] for a in self.attributes],
            "links": {"self": "/areatypes"}
        })

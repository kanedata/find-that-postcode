import bottle

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import *
import controllers.areas

class Areatype(Controller):

    es_type = 'code'
    url_slug = 'areatypes'

    def __init__(self, config):
        self.areatypes = {i[0]:i for i in AREA_TYPES}
        super().__init__(config)

    def get_by_id(self, areatype, p=1, size=None):
        self.set_from_data(areatype)
        self.areas = []
        if self.config.get("es") and not self.config.get("stop_recursion"):
            self.relationships["areas"] = []
            self.pagination = Pagination()
            query = {
                "query": {
                    "match": {
                        "type": self.id
                    }
                },
                "sort": [
                    {"sort_order.keyword": "asc" } # @TODO sort by _id? ??
                ]
            }
            result = self.config.get("es").search(index=self.config.get("es_index"), doc_type=self.es_type, body=query, from_=self.pagination.from_, size=self.pagination.size, _source_exclude=["boundary"])
            if result["hits"]["total"]>0:
                self.config["stop_recursion"] = True
                self.relationships["areas"] = [controllers.areas.Area(self.config).set_from_data(a) for a in result["hits"]["hits"]]
                self.attributes["count_areas"] = result["hits"]["total"]
                self.pagination.set_pagination(self.attributes["count_areas"])
            else: self.found = False
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

    def return_result(self, filetype):
        json = self.toJSON()
        if not self.found:
            return bottle.abort(404)

        if filetype=="html":
            return bottle.template(self.template_name(),
                result=self.areas,
                count_areas = self.attributes["count_areas"],
                page=self.p, size=self.size, from_=self.get_from(),
                pagination=self.pagination,
                area_type=[self.id, self.name, self.full_name, self.description],
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {
                "data": json[1],
                "included": json[2],
                "links": {
                    "self": self.url(),
                    "html": self.url("html")
                }
            }

class Areatypes(Controller):

    es_type = 'code'
    url_slug = 'areatypes'
    template = 'areatypes.html'

    def __init__(self, config, data=None):
        self.areatypes = {i[0]:i for i in AREA_TYPES}
        super().__init__(config, data)

    def get(self):
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
        self.area_counts = {i["key"]:i["doc_count"] for i in result["aggregations"]["group_by_type"]["buckets"]}
        self.attributes = []
        for a in self.areatypes:
            areatype = Areatype(self.config, a)
            if a in self.area_counts:
                areatype.attributes["count_areas"] = self.area_counts[a]
            self.attributes.append(areatype)

    def toJSON(self):
        return {
            "data": [a.toJSON() for a in self.attributes],
            "links": {"self": "/areatypes"}
        }

    def return_result(self, filetype):

        if filetype=="html":
            return bottle.template('areatypes.html',
                area_counts=self.area_counts,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        else:
            return self.toJSON()

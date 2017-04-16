import bottle

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import Controller
from .areas import get_area_link
from .areas import get_area_object

class Areatype(Controller):

    es_type = 'code'
    url_slug = 'areatypes'
    template = 'areatype.html'

    def __init__(self, es, es_index):
        super().__init__(es, es_index)

    def get(self, areatype, p, size):
        self.set_pages(p, size)
        query = {
            "query": {
                "match": {
                    "type": areatype
                }
            },
            "sort": [
                {"sort_order.keyword": "asc" } # @TODO sort by _id? ??
            ]
        }
        result = self.es.search(index=self.es_index, doc_type=self.es_type, body=query, from_=self.get_from(), size=self.size, _source_exclude=["boundary"])
        if result["hits"]["total"]>0:
            self.found = True
            self.id = areatype
            self.areas = result["hits"]["hits"]
            self.count_areas = result["hits"]["total"]
            self.set_pagination(self.count_areas)
            typedata = self.get_area_type(areatype)
            if typedata:
                self.name = typedata[1]
                self.full_name = typedata[2]
                self.description = typedata[3]
            else:
                self.name = areatype
                self.full_name = areatype
                self.description = ''

    def jsonapi(self):
        return {
            "type": "areatypes",
            "id": self.id,
            "attributes": {
                "name": self.name,
                "name_full": self.full_name,
                "description": self.description,
                "count": self.count_areas
            },
            "relationships": {
                "links": {
                    "self": self.url()
                }
            }
        }

    def return_result(self, filetype):
        if not self.found:
            return bottle.abort(404)

        if filetype=="html":
            return bottle.template(self.template_name(),
                result=self.areas,
                count_areas = self.count_areas,
                page=self.p, size=self.size, from_=self.get_from(),
                pagination=self.pagination,
                area_type=[self.id, self.name, self.full_name, self.description],
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            areatype_json = self.jsonapi()
            areatype_json["relationships"] = {
                "areas": {
                    "data": [{
                        "type": "areas",
                        "id": a["_id"]
                    } for a in self.areas],
                    "links": {
                        "self": self.relationship_url('areas', False),
                        "related": self.relationship_url('areas', True)
                    }
                }
            }
            links = self.pagination
            links["self"] = self.url()
            return {
                "data": areatype_json,
                "links": links,
                "included": [self.get_area_object(a) for a in self.areas]
            }

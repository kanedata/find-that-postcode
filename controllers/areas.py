from metadata import AREA_TYPES

from .controller import *
import controllers.postcodes
import controllers.areatypes

class Area(Controller):

    es_type = 'code'
    url_slug = 'areas'
    template = 'area.html'

    def __init__(self, config):
        super().__init__(config)
        self.boundary = None

    def get_by_id(self, id, boundary=False, examples_count=5):
        id = self.parse_id(id)
        _source_exclude = [] if boundary else ["boundary"]
        result = self.config.get("es").get(index=self.config.get("es_index"), doc_type=self.es_type, id=id, ignore=[404], _source_exclude=_source_exclude)
        if result["found"]:
            self.relationships["areatype"] = {}
            self.boundary = result["_source"].get("boundary")
            self.set_from_data(result)
            if examples_count>0:
                self.relationships["example_postcodes"] = self.get_example_postcodes(examples_count)

    def process_attributes(self, area):
        self.relationships["areatype"] = controllers.areatypes.Areatype(self.config).get_by_id(area["type"])
        del area["type"]
        if "boundary" in area:
            del area["boundary"]
        return area

    def get_example_postcodes(self, examples_count=5):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "query_string": {
                            "query": self.id
                        }
                    },
                    "random_score": {}
                }

            }
        }
        example = self.config.get("es").search(index=self.config.get("es_index"), doc_type='postcode', body=query, size=examples_count)
        return [controllers.postcodes.Postcode(self.config).set_from_data(e) for e in example["hits"]["hits"]]

    def topJSON(self):
        json = super().topJSON()
        if self.found:
            # @TODO need to check whether boundary data actually exists before applying this
            json[1]["links"]["geojson"] = self.url(filetype="geojson" )
        return json

    def geoJSON(self):
        if not self.boundary:
            bottle.abort(404, "boundary not found")
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": GEOJSON_TYPES[self.boundary["type"]],
                        "coordinates": self.boundary["coordinates"]
                    },
                    "properties": self.attributes
                }
            ]
        }

class Areas(Controller):

    es_type = 'code'
    url_slug = 'areas'

    def __init__(self, config):
        super().__init__(config)
        self.data = []
        self.meta = {}

    def search(self, q):
        self.pagination = Pagination()
        if q:
            self.meta["q"] = q
            result = self.config.get("es").search(index=self.config.get("es_index", "postcode"), doc_type=self.es_type, q=q, from_=self.pagination.from_, size=self.pagination.size, _source_exclude=["boundary"])
            self.data = [Area(self.config).set_from_data(a) for a in result["hits"]["hits"]]
            self.meta["result_count"] = result["hits"]["total"]

    def topJSON(self):
        # get all areatypes first
        ats = controllers.areatypes.Areatypes( self.config )
        ats.get()
        included = []
        for a in ats.attributes:
            included.append(a.toJSON()[1])

        return (200, {
            "data": [a.toJSON()[1] for a in self.data],
            "meta": self.pagination.get_meta(self.meta),
            "links": self.pagination.get_links({}),
            "included": included
        })

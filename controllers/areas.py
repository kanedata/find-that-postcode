from elasticsearch.helpers import scan

from .controller import Controller, Pagination, GEOJSON_TYPES
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
            if examples_count > 0:
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
            if json[1]["data"]["attributes"].get("has_boundary"):
                json[1]["links"]["geojson"] = self.url(filetype="geojson")
        return json

    def geoJSON(self):
        if not self.boundary:
            return (404, "boundary not found")
        return (200, {
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
        })


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
            query = {
                "query": {
                    "function_score": {
                        "query": {
                            "query_string": {
                                "query": q
                            }
                        },
                        "boost": "5",
                        "functions": [
                            {"weight": 3, "filter": {"terms": {"type": ["ctry", "region", "cty", "laua", "rgn"]}}},
                            {"weight": 2, "filter": {"terms": {"type": ["ttwa", "pfa", "lep", "park", "pcon"]}}},
                            {"weight": 1.5, "filter": {"terms": {"type": ["ccg", "hlthau", "hro", "pct"]}}},
                            {"weight": 1, "filter": {"terms": {"type": ["eer", "bua11", "buasd11", "teclec"]}}},
                            {"weight": 0.4, "filter": {"terms": {"type": ["msoa11", "lsoa11", "wz11", "oa11", "nuts", "ward"]}}}
                        ]
                    }
                }
            }
            result = self.config.get("es").search(
                index=self.config.get("es_index", "postcode"), 
                doc_type=self.es_type, 
                body=query, 
                from_=self.pagination.from_, 
                size=self.pagination.size, 
                _source_exclude=["boundary"], 
                ignore=[400]
            )
            self.data = [Area(self.config).set_from_data(a) for a in result.get("hits", {}).get("hits", [])]
            self.meta["result_count"] = result.get("hits", {}).get("total", 0)

    def get_all(self, area_types=None):
        q = None
        if area_types:
            q = {
                "query": {
                    "terms": {
                        "type": area_types
                    }
                }
            }
        result = scan(
            self.config.get("es"),
            query=q,
            index=self.config.get("es_index", "postcode"), 
            doc_type=self.es_type, 
            _source_include=["type", "name"], 
            size=10000,
            ignore=[400]
        )
        for r in result:
            yield {
                "code": r["_id"], 
                "name": r["_source"]["name"],
                "type": r["_source"]["type"]
            }


    def topJSON(self):
        # get all areatypes first
        ats = controllers.areatypes.Areatypes(self.config)
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

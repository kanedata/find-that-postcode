from elasticsearch.helpers import scan

from .controller import Controller, Pagination, GEOJSON_TYPES
from . import postcodes
from . import areatypes


class Area(Controller):

    es_index = 'geo_area'
    url_slug = 'areas'
    template = 'area.html'

    def __init__(self, id, data=None, entity=None, example_postcodes=None, boundary=None):
        super().__init__(id, data)
        self.example_postcodes = example_postcodes
        self.entity = entity
        self.boundary = boundary

    def __repr__(self):
        return '<Area {}>'.format(self.id)

    @classmethod
    def get_from_es(cls, id, es, es_config=None, examples_count=5, boundary=False):
        if not es_config:
            es_config = {}

        # fetch the initial area
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_exclude=[] if boundary else ["boundary"],
        )
        entity = {}
        if data["found"] and data["_source"].get("entity"):
            entity = es.get(index="geo_entity", doc_type="_doc", id=data["_source"].get("entity"))

        postcodes = []
        if examples_count:
            postcodes = cls.get_example_postcodes(id, es, examples_count=examples_count)
        
        return cls(
            data.get("_id"),
            data.get("_source"),
            areatypes.Areatype(entity.get("_id"), entity.get("_source")),
            postcodes,
            data.get("_source", {}).get("boundary")
        )

    def process_attributes(self, area):
        # self.relationships["areatype"] = areatypes.Areatype(self.config, self.es).get_by_id(area.get("type"))
        # del area["type"]
        if "boundary" in area:
            del area["boundary"]
        return area

    @classmethod
    def get_example_postcodes(areacode, es, examples_count=5):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "query_string": {
                            "query": areacode
                        }
                    },
                    "random_score": {}
                }

            }
        }
        example = es.search(index='geo_postcode', doc_type='_doc', body=query, size=examples_count)
        return [postcodes.Postcode(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

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

    es_index = 'geo_area'
    url_slug = 'areas'

    def __init__(self, config, es):
        super().__init__(config, es)
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
            result = self.es.search(
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
            self.es,
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

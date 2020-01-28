from datetime import datetime

from elasticsearch.helpers import scan
import shapely.wkt
import shapely.geometry

from .controller import Controller, Pagination, GEOJSON_TYPES
from . import postcodes
from . import areatypes
from . import places


class Area(Controller):

    es_index = 'geo_area'
    url_slug = 'areas'
    template = 'area.html'
    date_fields = ['date_end', 'date_start']

    def __init__(self, id, data=None, **kwargs):
        super().__init__(id)
        self.relationships["example_postcodes"] = kwargs.get("example_postcodes")
        self.relationships["areatype"] = kwargs.get("areatype")
        self.relationships["parent"] = kwargs.get("parent")
        self.relationships["predecessor"] = kwargs.get("predecessor")
        self.relationships["successor"] = kwargs.get("successor")
        self.relationships["children"] = kwargs.get("children")
        self.boundary = kwargs.get("boundary")
        if data:
            self.found = True
            self.attributes = self.process_attributes(data)

    def __repr__(self):
        return '<Area {}>'.format(self.id)

    @classmethod
    def get_from_es(cls, id, es, es_config=None, examples_count=5, boundary=False, recursive=True):
        if not es_config:
            es_config = {}

        # fetch the initial area
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_excludes=([] if boundary else ["boundary"]),
        )
        relationships = {
            "areatype": {},
            "example_postcodes": [],
            "boundary": data.get("_source", {}).get("boundary"),
        }
        if data["found"]:
            if data["_source"].get("type"):
                relationships["areatype"] = areatypes.Areatype(data["_source"].get("type"))
            elif data["_source"].get("entity"):
                relationships["areatype"] = areatypes.Areatype.get_from_es(data["_source"].get("entity"), es)

        if examples_count:
            relationships["example_postcodes"] = cls.get_example_postcodes(id, es, examples_count=examples_count)

        if data.get("_source", {}) and recursive:
            children = cls.get_children(id, es)
            data["_source"]["child_count"] = children["total"]
            relationships["children"] = children["areas"]
            data["_source"]["child_counts"] = children["counts"]

        if data.get("_source", {}).get("parent") and recursive:
            relationships["parent"] = cls.get_from_es(data["_source"]["parent"], es, examples_count=0, recursive=False)

        if data.get("_source", {}).get("predecessor") and recursive:
            relationships["predecessor"] = [
                cls.get_from_es(i, es, examples_count=0, recursive=False)
                for i in data["_source"]["predecessor"]
            ]

        if data.get("_source", {}).get("successor") and recursive:
            relationships["successor"] = [
                cls.get_from_es(i, es, examples_count=0, recursive=False)
                for i in data["_source"]["successor"] if i
            ]

        return cls(
            data.get("_id"),
            data=data.get("_source"),
            **relationships
        )

    def process_attributes(self, data):
        if not self.relationships.get("areatype") and data.get("type"):
            self.relationships["areatype"] = areatypes.Areatype(data.get("type"))
        if "type" in data:
            del data["type"]
        if "boundary" in data:
            if not self.boundary:
                self.boundary = data["boundary"]
            del data["boundary"]

        # turn dates into dates
        for i in self.date_fields:
            if data.get(i) and not isinstance(data[i], datetime):
                try:
                    data[i] = datetime.strptime(data[i][0:10], "%Y-%m-%d")
                except ValueError:
                    continue
        return data

    @staticmethod
    def get_example_postcodes(areacode, es, examples_count=5):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must_not": {
                                "exists": {
                                    "field": "doterm"
                                }
                            },
                            "must": {
                                "query_string": {
                                    "query": areacode
                                }
                            }
                        }
                    },
                    "random_score": {}
                }
            }
        }
        example = es.search(index='geo_postcode', body=query, size=examples_count)

        # if len(example["hits"]["hits"]) == 0:
        #     query = {
        #         "query": {
        #             "function_score": {
        #                 "query": {
        #                     "bool": {
        #                         "must_not": {
        #                             "exists": {
        #                                 "field": "doterm"
        #                             }
        #                         },
        #                         "filter": {
        #                             "geo_shape": {
        #                                 "location": {
        #                                     "indexed_shape": {
        #                                         "index": "geo_area",
        #                                         "id": areacode,
        #                                         "path": "boundary"
        #                                     }
        #                                 }
        #                             }
        #                         }
        #                     }
        #                 },
        #                 "random_score": {}
        #             }
        #         }
        #     }
        #     example = es.search(index='geo_postcode',
        #                         body=query, size=examples_count)


        return [postcodes.Postcode(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    @staticmethod
    def get_children(areacode, es):
        query = {
            "aggs": {
                "types": {
                    "terms": {"field": "type.keyword"}
                }
            },
            "query": {
                "function_score": {
                    "query": {
                        "match": {
                            "parent": {
                                "query": areacode
                            }
                        },
                    },
                    "random_score": {}
                }
            }
        }
        children = es.search(index='geo_area', body=query, size=10, _source_includes=['code', 'name', 'type'])
        return {
            "total": Area.get_total_from_es(children),
            "areas": {
                t["key"]: [Area(e["_id"], e["_source"]) for e in children["hits"]["hits"] if e["_source"].get("type") == t["key"]]
                for t in children.get("aggregations", {}).get("types", {}).get("buckets", [])
            },
            "counts": {
                t["key"]: t["doc_count"]
                for t in children.get("aggregations", {}).get("types", {}).get("buckets", [])
            }
        }

    def topJSON(self):
        json = super().topJSON()
        if self.found:
            # @TODO need to check whether boundary data actually exists before applying this
            if json["data"]["attributes"].get("has_boundary"):
                json["links"]["geojson"] = self.url(filetype="geojson")
        return json

    def geoJSON(self):
        if not self.boundary:
            return (404, "boundary not found")

        if not isinstance(self.boundary, dict):
            # assume boundary is a WKT string if not a dictionary
            s = shapely.wkt.loads(self.boundary)
            self.boundary = shapely.geometry.mapping(s)

        return (200, {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": GEOJSON_TYPES.get(self.boundary["type"], self.boundary["type"]),
                        "coordinates": self.boundary["coordinates"]
                    },
                    "properties": self.attributes
                }
            ]
        })


def search_areas(q, es, pagination=None, es_config=None):
    """
    Search for areas based on a name
    """
    if not es_config:
        es_config = {}
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
                    {"weight": 0.1, "filter": {"term": {"active": False}}},
                    {"weight": 6, "filter": {"exists": {"field": "type"}}},
                    {"weight": 3, "filter": {"terms": {"type": ["ctry", "region", "cty", "laua", "rgn", "LOC"]}}},
                    {"weight": 2, "filter": {"terms": {"type": ["ttwa", "pfa", "lep", "park", "pcon"]}}},
                    {"weight": 1.5, "filter": {"terms": {"type": ["ccg", "hlthau", "hro", "pct"]}}},
                    {"weight": 1, "filter": {"terms": {"type": ["eer", "bua11", "buasd11", "teclec"]}}},
                    {"weight": 0.4, "filter": {"terms": {"type": ["msoa11", "lsoa11", "wz11", "oa11", "nuts", "ward"]}}}
                ]
            }
        }
    }
    if pagination:
        result = es.search(
            index="geo_area,geo_placename",
            body=query,
            from_=pagination.from_,
            size=pagination.size,
            _source_excludes=["boundary"],
            ignore=[404]
        )
    else:
        result = es.search(
            index="geo_area,geo_placename",
            body=query,
            _source_excludes=["boundary"],
            ignore=[404]
        )
    return_result = []
    for a in result.get("hits", {}).get("hits", []):
        if a["_index"] == 'geo_placename':
            return_result.append(places.Place(a["_id"], a["_source"]))
        else:
            return_result.append(Area(a["_id"], a["_source"]))
    total = result.get("hits", {}).get("total", 0)
    if isinstance(total, dict):
        total = total.get("value", 0)
    return {
        "result": return_result,
        "scores": [a["_score"] for a in result.get("hits", {}).get("hits", [])],
        "result_count": total,
    }


def get_all_areas(es, areatypes=None, es_config=None):
    """
    Search for areas based on a name
    """
    if not es_config:
        es_config = {}
    query = {
        "match_all": {}
    }
    if areatypes:
        query = {
            "terms": {
                "type": areatypes
            }
        }
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "term": {
                        "name.keyword": ""
                    }
                },
                "must": query
            }
        }
    }
    result = scan(
        es,
        query=query,
        index=es_config.get("es_index", Area.es_index),
        _source_include=["type", "name"],
        ignore=[400]
    )

    for r in result:
        yield {
            "code": r["_id"],
            "name": r["_source"]["name"],
            "type": r["_source"]["type"]
        }

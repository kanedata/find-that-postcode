import io
import json
from datetime import datetime

from botocore.exceptions import ClientError
from elasticsearch.helpers import scan
from flask import current_app

from ..db import get_s3_client
from . import areatypes, places, postcodes
from .controller import GEOJSON_TYPES, Controller


class Area(Controller):
    es_index = "geo_area"
    url_slug = "areas"
    template = "area.html.j2"
    date_fields = ["date_end", "date_start"]

    def __init__(self, id, data=None, **kwargs):
        super().__init__(id)
        self.relationships["example_postcodes"] = kwargs.get("example_postcodes")
        self.relationships["areatype"] = kwargs.get("areatype")
        self.relationships["parent"] = kwargs.get("parent")
        self.relationships["predecessor"] = kwargs.get("predecessor")
        self.relationships["successor"] = kwargs.get("successor")
        self.relationships["children"] = kwargs.get("children")
        self._boundary = None
        if data:
            self.found = True
            self.attributes = self.process_attributes(data)

    def __repr__(self):
        return "<Area {}>".format(self.id)

    @classmethod
    def get_from_es(
        cls, id, es, es_config=None, examples_count=5, boundary=False, recursive=True
    ):
        if not es_config:
            es_config = {}

        # fetch the initial area
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_excludes=(["boundary"]),
        )
        relationships = {
            "areatype": {},
            "example_postcodes": [],
        }
        if data["found"]:
            if data["_source"].get("type"):
                relationships["areatype"] = areatypes.Areatype(
                    data["_source"].get("type")
                )
            elif data["_source"].get("entity"):
                relationships["areatype"] = areatypes.Areatype.get_from_es(
                    data["_source"].get("entity"), es
                )

        if examples_count:
            relationships["example_postcodes"] = cls.get_example_postcodes(
                id, es, examples_count=examples_count
            )

        if data.get("_source", {}) and recursive:
            children = cls.get_children(id, es)
            data["_source"]["child_count"] = children["total"]
            relationships["children"] = children["areas"]
            data["_source"]["child_counts"] = children["counts"]

        if data.get("_source", {}).get("parent") and recursive:
            relationships["parent"] = cls.get_from_es(
                data["_source"]["parent"], es, examples_count=0, recursive=False
            )

        if data.get("_source", {}).get("predecessor") and recursive:
            relationships["predecessor"] = [
                cls.get_from_es(i, es, examples_count=0, recursive=False)
                for i in data["_source"]["predecessor"]
            ]

        if data.get("_source", {}).get("successor") and recursive:
            relationships["successor"] = [
                cls.get_from_es(i, es, examples_count=0, recursive=False)
                for i in data["_source"]["successor"]
                if i
            ]

        return cls(data.get("_id"), data=data.get("_source"), **relationships)

    def process_attributes(self, data):
        if not self.relationships.get("areatype") and data.get("type"):
            self.relationships["areatype"] = areatypes.Areatype(data.get("type"))
        if "type" in data:
            del data["type"]

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
                            "must_not": {"exists": {"field": "doterm"}},
                            "must": {"query_string": {"query": areacode}},
                        }
                    },
                    "random_score": {},
                }
            }
        }
        example = es.search(index="geo_postcode", body=query, size=examples_count)

        return [
            postcodes.Postcode(e["_id"], e["_source"]) for e in example["hits"]["hits"]
        ]

    @staticmethod
    def get_children(areacode, es):
        query = {
            "aggs": {"types": {"terms": {"field": "type.keyword"}}},
            "query": {
                "function_score": {
                    "query": {
                        "match": {"parent": {"query": areacode}},
                    },
                    "random_score": {},
                }
            },
        }
        children = es.search(
            index="geo_area",
            body=query,
            size=100,
            _source_includes=["code", "name", "type", "active"],
        )
        return {
            "total": Area.get_total_from_es(children),
            "areas": {
                t["key"]: [
                    Area(e["_id"], e["_source"])
                    for e in children["hits"]["hits"]
                    if e["_source"].get("type") == t["key"]
                ]
                for t in children.get("aggregations", {})
                .get("types", {})
                .get("buckets", [])
            },
            "counts": {
                t["key"]: t["doc_count"]
                for t in children.get("aggregations", {})
                .get("types", {})
                .get("buckets", [])
            },
        }

    @property
    def boundary(self):
        if self._boundary is None:
            self._boundary = self._get_boundary()
        return self._boundary

    @property
    def has_boundary(self):
        if self._boundary is None:
            self._boundary = self._get_boundary()
        return self._boundary is not None

    def _get_boundary(self):
        client = get_s3_client()
        buffer = io.BytesIO()
        area_code = self.id
        prefix = self.id[0:3]
        try:
            client.download_fileobj(
                current_app.config["S3_BUCKET"],
                "%s/%s.json" % (prefix, area_code),
                buffer,
            )
            boundary = json.loads(buffer.getvalue().decode("utf-8"))
            return boundary.get("geometry")
        except ClientError:
            None

    def topJSON(self):
        json = super().topJSON()
        if self.found:
            # @TODO need to check whether boundary data
            # actually exists before applying this
            if self.has_boundary:
                json["links"]["geojson"] = self.url(filetype="geojson")
        return json

    def geoJSON(self):
        if not self.boundary:
            return (404, "boundary not found")

        return (
            200,
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": GEOJSON_TYPES.get(
                                self.boundary["type"], self.boundary["type"]
                            ),
                            "coordinates": self.boundary["coordinates"],
                        },
                        "properties": self.attributes,
                    }
                ],
            },
        )


def search_areas(q, es, pagination=None, es_config=None):
    """
    Search for areas based on a name
    """
    if not es_config:
        es_config = {}
    query = {
        "query": {
            "function_score": {
                "query": {"query_string": {"query": q}},
                "boost": "5",
                "functions": [
                    {"weight": 0.1, "filter": {"term": {"active": False}}},
                    {"weight": 6, "filter": {"exists": {"field": "type"}}},
                    {
                        "weight": 3,
                        "filter": {
                            "terms": {
                                "type": [
                                    "ctry",
                                    "region",
                                    "cty",
                                    "laua",
                                    "rgn",
                                    "LOC",
                                    "ward",
                                ]
                            }
                        },
                    },
                    {
                        "weight": 2,
                        "filter": {
                            "terms": {"type": ["ttwa", "pfa", "lep", "park", "pcon"]}
                        },
                    },
                    {
                        "weight": 1.5,
                        "filter": {"terms": {"type": ["ccg", "hlthau", "hro", "pct"]}},
                    },
                    {
                        "weight": 1,
                        "filter": {
                            "terms": {"type": ["eer", "bua11", "buasd11", "teclec"]}
                        },
                    },
                    {
                        "weight": 0.4,
                        "filter": {
                            "terms": {
                                "type": [
                                    "msoa11",
                                    "lsoa11",
                                    "msoa21",
                                    "lsoa21",
                                    "wz11",
                                    "oa11",
                                    "oa21",
                                    "nuts",
                                    "ward",
                                ]
                            }
                        },
                    },
                ],
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
            ignore=[404],
        )
    else:
        result = es.search(
            index="geo_area,geo_placename",
            body=query,
            _source_excludes=["boundary"],
            ignore=[404],
        )
    return_result = []
    for a in result.get("hits", {}).get("hits", []):
        if a["_index"] == "geo_placename":
            relationships = {}
            if a["_source"].get("areas", {}).get("laua"):
                relationships["areas"] = [
                    Area.get_from_es(
                        a["_source"]["areas"]["laua"],
                        es,
                        examples_count=0,
                        recursive=False,
                    )
                ]
            return_result.append(places.Place(a["_id"], a["_source"], **relationships))
        else:
            relationships = {}
            if a["_source"].get("parent"):
                relationships["parent"] = Area.get_from_es(
                    a["_source"]["parent"], es, examples_count=0, recursive=False
                )
            return_result.append(Area(a["_id"], a["_source"], **relationships))
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
    query = {"match_all": {}}
    if areatypes:
        query = {"terms": {"type": areatypes}}
    query = {
        "query": {"bool": {"must_not": {"term": {"name.keyword": ""}}, "must": query}}
    }
    result = scan(
        es,
        query=query,
        index=es_config.get("es_index", Area.es_index),
        _source_includes=["type", "name", "active", "date_start", "date_end"],
        ignore=[400],
    )

    for r in result:
        yield {
            "code": r["_id"],
            "name": r["_source"]["name"],
            "type": r["_source"]["type"],
            "active": r["_source"].get("active"),
            "date_start": r["_source"].get("date_start"),
            "date_end": r["_source"].get("date_end"),
        }

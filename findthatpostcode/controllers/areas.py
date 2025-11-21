import io
import json
from datetime import datetime
from typing import TYPE_CHECKING, Generator

from botocore.exceptions import ClientError
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from mypy_boto3_s3 import S3Client

from findthatpostcode.areatypes import AREA_TYPES, AreaTypeEnum
from findthatpostcode.controllers.controller import (
    GEOJSON_TYPES,
    Controller,
    Pagination,
)
from findthatpostcode.controllers.places import Place
from findthatpostcode.settings import (
    AREA_INDEX,
    ENTITY_INDEX,
    PLACENAME_INDEX,
    POSTCODE_INDEX,
    S3_BUCKET,
)
from findthatpostcode.utils import ESConfig

if TYPE_CHECKING:
    from findthatpostcode.controllers.postcodes import Postcode


class Areatype(Controller):
    es_index = ENTITY_INDEX
    url_slug = "areatypes"
    areatypes = AREA_TYPES

    def __init__(self, id: str, data: dict | None = None) -> None:
        id_areatype = self.check_id(id)
        if not data and id_areatype:
            data = self.areatypes.get(id_areatype)
        super().__init__(id_areatype.value, data)
        if not isinstance(self.id, str):
            raise ValueError("ID must be a string to create Areatype")

    @staticmethod
    def check_id(id: str) -> AreaTypeEnum:
        id = id.strip()
        try:
            id_areatype = AreaTypeEnum(id)
        except ValueError:
            id_areatype = None
            for at, at_data in Areatype.areatypes.items():
                if id in at_data.get("entities", []):
                    id_areatype = at
                    break
        if not id_areatype:
            raise ValueError(f"Invalid AreaType ID: {id}")
        return id_areatype

    def __repr__(self) -> str:
        return "<AreaType {}>".format(self.id)

    def process_attributes(self, data: dict | list | tuple) -> dict:
        if isinstance(data, (list, tuple)):
            return {
                "code": data[0],
                "entities": data[1],
                "name": data[2],
                "full_name": data[3],
                "description": data[4],
                "abbreviation": data[0],
            }
        return data

    def get_name(self, country: str | None = None) -> str | None:
        if not isinstance(self.id, str):
            return None
        if isinstance(country, str):
            country = country[0].upper()
        if self.id.startswith("lsoa") and country == "S":
            return "Data Zone"
        if self.id.startswith("lsoa") and country == "N":
            return "Super Output Area"
        if self.id.startswith("msoa") and country == "S":
            return "Intermediate Zone"

        name = self.attributes.get("name")
        if isinstance(name, str):
            return name
        return None

    @classmethod
    def get_from_es(
        cls: type["Areatype"],
        id: str,
        es: Elasticsearch,
        es_config: ESConfig | None = None,
        full: bool = False,
    ) -> "Areatype":
        id_areatype = cls.check_id(id)
        if cls.areatypes.get(id_areatype):
            return cls(id)
        result = super(Areatype, cls).get_from_es(id, es, es_config=es_config)
        if not isinstance(result.id, str):
            raise ValueError("ID must be a string to create Areatype")
        return cls(result.id, result.attributes)

    def get_areas(
        self: "Areatype",
        es: Elasticsearch,
        es_config: ESConfig | None = None,
        pagination: Pagination | None = None,
    ) -> None:
        query = {
            "query": {
                "function_score": {
                    "query": {"match": {"type": self.id}},
                    "random_score": {},
                }
            }
        }
        search_params: dict[str, str | dict | int] = dict(
            index=AREA_INDEX,
            body=query,
            sort="_id:asc",
        )
        if (
            pagination
            and isinstance(pagination.from_, int)
            and isinstance(pagination.size, int)
        ):
            search_params["from_"] = pagination.from_
            search_params["size"] = pagination.size
        example = es.search(**search_params)
        if not isinstance(example, dict):
            return
        self.relationships["areas"] = [
            Area(e["_id"], e["_source"]) for e in example["hits"]["hits"]
        ]
        self.attributes["count_areas"] = self.get_total_from_es(example)


def area_types_count(
    es: Elasticsearch, es_config: ESConfig | None = None
) -> dict[str, int]:
    if not es_config:
        es_config = ESConfig(es_index=Area.es_index)

    # fetch counts per entity
    query = {
        "size": 0,
        "aggs": {"group_by_type": {"terms": {"field": "type.keyword", "size": 100}}},
    }
    result = es.search(
        index=es_config.es_index,
        body=query,
        ignore=[404],  # type: ignore
        _source_includes=[],  # type: ignore
    )
    return {
        i["key"]: i["doc_count"]
        for i in result.get("aggregations", {})
        .get("group_by_type", {})
        .get("buckets", [])
    }


class Area(Controller):
    es_index = AREA_INDEX
    url_slug = "areas"
    template = "area.html.j2"
    date_fields = ["date_end", "date_start"]

    def __init__(
        self: "Area",
        id: str,
        data: dict | None = None,
        s3_client: S3Client | None = None,
        **kwargs,
    ) -> None:
        super().__init__(id)
        if not isinstance(self.id, str):
            raise ValueError("ID must be a string to create URL")
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

        self._s3_client = s3_client

    def __repr__(self: "Area") -> str:
        return "<Area {}>".format(self.id)

    @staticmethod
    def parse_id(id: str | tuple[float, float]) -> str | tuple[float, float]:
        return id.strip().upper() if isinstance(id, str) else id

    @classmethod
    def get_from_es(
        cls: type["Area"],
        id: str,
        es: Elasticsearch,
        es_config: ESConfig | None = None,
        examples_count: int = 5,
        boundary: bool = False,
        recursive: bool = True,
        s3_client: S3Client | None = None,
    ) -> "Area":
        if not es_config:
            es_config = ESConfig(es_index=cls.es_index, es_type=cls.es_type)

        # fetch the initial area
        data = es.get(
            index=es_config.es_index,
            doc_type=es_config.es_type,
            id=cls.parse_id(id),
            ignore=[404],  # type: ignore
            _source_excludes=(["boundary"]),  # type: ignore
        )
        relationships = {
            "areatype": {},
            "example_postcodes": [],
        }
        if data["found"]:
            if data["_source"].get("type"):
                relationships["areatype"] = Areatype(data["_source"].get("type"))
            elif data["_source"].get("entity"):
                relationships["areatype"] = Areatype.get_from_es(
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
                data["_source"]["parent"],
                es,
                examples_count=0,
                recursive=False,
                s3_client=s3_client,
            )

        if data.get("_source", {}).get("predecessor") and recursive:
            relationships["predecessor"] = [
                cls.get_from_es(
                    i, es, examples_count=0, recursive=False, s3_client=s3_client
                )
                for i in data["_source"]["predecessor"]
            ]

        if data.get("_source", {}).get("successor") and recursive:
            relationships["successor"] = [
                cls.get_from_es(
                    i, es, examples_count=0, recursive=False, s3_client=s3_client
                )
                for i in data["_source"]["successor"]
                if i
            ]

        return cls(
            data.get("_id"),
            data=data.get("_source"),
            s3_client=s3_client,
            **relationships,
        )

    def process_attributes(self: "Area", data: dict) -> dict:
        if not isinstance(self.id, str):
            raise ValueError("ID must be a string to process attributes")

        areatype = data.get("type")
        if not self.relationships.get("areatype") and isinstance(areatype, str):
            self.relationships["areatype"] = Areatype(areatype)
        if "type" in data:
            del data["type"]

        # turn dates into dates
        for i in self.date_fields:
            if data.get(i) and not isinstance(data[i], datetime):
                try:
                    data[i] = datetime.strptime(data[i][0:10], "%Y-%m-%d")
                except ValueError:
                    continue

        if self.id.startswith("E"):
            data["ctry"] = "E92000001"
            data["ctry_name"] = "England"
        elif self.id.startswith("W"):
            data["ctry"] = "W92000004"
            data["ctry_name"] = "Wales"
        elif self.id.startswith("S"):
            data["ctry"] = "S92000003"
            data["ctry_name"] = "Scotland"
        elif self.id.startswith("N"):
            data["ctry"] = "N92000002"
            data["ctry_name"] = "Northern Ireland"

        return data

    @staticmethod
    def get_example_postcodes(
        areacode: str, es: Elasticsearch, examples_count: int = 5
    ) -> list["Postcode"]:
        from findthatpostcode.controllers.postcodes import Postcode

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
        example = es.search(
            index=POSTCODE_INDEX,
            body=query,
            size=examples_count,  # type: ignore
        )

        return [Postcode(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    @staticmethod
    def get_children(areacode: str, es: Elasticsearch) -> dict:
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
            index=AREA_INDEX,
            body=query,
            size=100,  # type: ignore
            _source_includes=["code", "name", "type", "active"],  # type: ignore
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
    def boundary(self: "Area") -> dict | None:
        if self._boundary is None:
            self._boundary = self._get_boundary()
        return self._boundary

    @property
    def has_boundary(self: "Area") -> bool:
        if self._boundary is None:
            self._boundary = self._get_boundary()
        return self._boundary is not None

    def _get_boundary(self: "Area") -> dict | None:
        if getattr(self, "_s3_client", None) is None or self._s3_client is None:
            raise ValueError("S3 client not set on Area instance")
        buffer = io.BytesIO()
        area_code = self.id
        prefix = self.id[0:3]
        try:
            self._s3_client.download_fileobj(
                S3_BUCKET,
                "%s/%s.json" % (prefix, area_code),
                buffer,
            )
            boundary = json.loads(buffer.getvalue().decode("utf-8"))
            return boundary.get("geometry")
        except ClientError:
            return None

    def topJSON(self: "Area") -> dict:
        json = super().topJSON()
        if self.found:
            # @TODO need to check whether boundary data
            # actually exists before applying this
            if self.has_boundary:
                json["links"]["geojson"] = self.url(filetype="geojson")
        return json

    def geoJSON(self: "Area") -> tuple[int, dict | str]:
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


def search_areas(
    q: str,
    es: Elasticsearch,
    pagination: Pagination | None = None,
    es_config: ESConfig | None = None,
) -> dict[str, object]:
    """
    Search for areas based on a name
    """
    if not es_config:
        es_config = ESConfig(es_index=AREA_INDEX)
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
            index=f"{AREA_INDEX},{PLACENAME_INDEX}",
            body=query,
            from_=pagination.from_,  # type: ignore
            size=pagination.size,  # type: ignore
            _source_excludes=["boundary"],  # type: ignore
            ignore=[404],  # type: ignore
        )
    else:
        result = es.search(
            index=f"{AREA_INDEX},{PLACENAME_INDEX}",
            body=query,
            _source_excludes=["boundary"],  # type: ignore
            ignore=[404],  # type: ignore
        )
    return_result = []
    for a in result.get("hits", {}).get("hits", []):
        if a["_index"] == PLACENAME_INDEX:
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
            return_result.append(Place(a["_id"], a["_source"], **relationships))
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


def get_all_areas(
    es: Elasticsearch,
    areatypes: list[str] | None = None,
    es_config: ESConfig | None = None,
) -> Generator[dict, None, None]:
    """
    Search for areas based on a name
    """
    if not es_config:
        es_config = ESConfig(es_index=Area.es_index)
    query = {"match_all": {}}
    if areatypes:
        query = {"terms": {"type": areatypes}}
    query = {
        "query": {"bool": {"must_not": {"term": {"name.keyword": ""}}, "must": query}}
    }
    result = scan(
        es,
        query=query,
        index=es_config.es_index,
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

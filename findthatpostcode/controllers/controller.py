import math
from http import HTTPStatus
from urllib.parse import ParseResult, urlencode, urlunparse

from elasticsearch import Elasticsearch

from findthatpostcode.utils import ESConfig

GEOJSON_TYPES = {
    "point": "Point",  # A single geographic coordinate.
    "linestring": "LineString",  # An arbitrary line given two or more points.
    "polygon": "Polygon",  # A closed polygon whose first and last point must match,
    # requiring n+1 vertices to create an n-sided
    # polygon and a minimum of 4 vertices.
    "multipoint": "MultiPoint",  # An array of unconnected, but likely related points.
    "multilinestring": "MultiLineString",  # An array of separate linestrings.
    "multipolygon": "MultiPolygon",  # An array of separate polygons.
    "geometrycollection": "GeometryCollection",  # A GeoJSON shape similar to the
    # multi* shapes except that multiple types can coexist
    # (e.g., a Point and a LineString).
}


class Controller:
    template: str | None = None
    es_index: str = "geo"
    es_type: str = "_doc"
    url_slug: str = "controllers"

    def __init__(
        self: "Controller", id: str | tuple[float, float], data: dict | None = None
    ):
        # main configuration
        self.urlparts: ParseResult | None = None
        self.found: bool = False
        self.errors: list[str] = []
        self.attributes: dict[str, object] = {}
        self.relationships: dict[str, object] = {}
        self.id: str | tuple[float, float] = self.parse_id(id)
        self.pagination: Pagination | None = None
        if data:
            self.found = True
            self.attributes = self.process_attributes(data)

    @classmethod
    def get_from_es(
        cls: type["Controller"],
        id: str,
        es: Elasticsearch,
        es_config: ESConfig | None = None,
    ):
        if not es_config:
            es_config = ESConfig(es_index=cls.es_index, es_type=cls.es_type)
        data = es.get(
            index=es_config.es_index,
            doc_type=es_config.es_type,
            id=cls.parse_id(id),
            ignore=[HTTPStatus.NOT_FOUND],  # type: ignore
            _source_excludes=es_config._source_exclude,  # type: ignore
        )
        return cls(data.get("_id"), data.get("_source"))

    def process_attributes(self: "Controller", data: dict) -> dict[str, object]:
        return data

    @staticmethod
    def parse_id(id: str | tuple[float, float]) -> str | tuple[float, float]:
        return id.strip() if isinstance(id, str) else id

    @staticmethod
    def get_total_from_es(result: dict) -> int | None:
        """
        Elasticsearch python seems to have changed how it returns the total number of
        hits in a search - this gets a consistent figure no matter the version
        """
        if isinstance(result["hits"]["total"], dict):
            return result["hits"]["total"]["value"]
        if isinstance(result["hits"]["total"], (float, int)):
            return result["hits"]["total"]
        return None

    def url(
        self: "Controller", filetype: str | None = None, query_vars: dict = {}
    ) -> str:
        if not isinstance(self.id, str):
            raise ValueError("ID must be a string to create URL")
        path = [
            self.url_slug,
            self.id.replace(" ", "+") + self.set_url_filetype(filetype),
        ]
        return urlunparse(
            [
                self.urlparts.scheme if self.urlparts else "",
                self.urlparts.netloc if self.urlparts else "",
                "/".join(path),
                "",
                self.get_query_string(query_vars),
                "",
            ]
        )

    def relationship_url(
        self: "Controller",
        relationship: str,
        related: bool = True,
        filetype: str | None = None,
        query_vars: dict = {},
    ) -> str:
        if not isinstance(self.id, str):
            raise ValueError("ID must be a string to create URL")
        if related:
            path = [
                self.url_slug,
                self.id.replace(" ", "+"),
                relationship + self.set_url_filetype(filetype),
            ]
        else:
            path = [
                self.url_slug,
                self.id.replace(" ", "+"),
                "relationships",
                relationship + self.set_url_filetype(filetype),
            ]
        return urlunparse(
            [
                self.urlparts.scheme if self.urlparts else "",
                self.urlparts.netloc if self.urlparts else "",
                "/".join(path),
                "",
                self.get_query_string(query_vars),
                "",
            ]
        )

    def set_url_filetype(self: "Controller", filetype: str | None = None) -> str:
        if filetype:
            return "." + filetype
        return ""

    def get_query_string(self: "Controller", query_vars: dict = {}) -> str:
        # query_vars = self.page_query_vars(query_vars)
        return urlencode(query_vars)

    def get_errors(self: "Controller") -> list[dict[str, str | int]]:
        if not self.found:
            return [
                {
                    "status": HTTPStatus.NOT_FOUND,
                    "title": "resource not found",
                    "detail": "resource could not be found",
                }
            ]
        return []

    # role = top|identifier|embedded
    def toJSON(self: "Controller", role: str = "top") -> tuple[dict, list]:
        json = {}
        included = []

        # check if anything has been found
        if not self.found:
            json["errors"] = self.get_errors()
            return (json, included)

        json["type"] = self.url_slug
        json["id"] = self.id
        if role == "identifer":
            return (json, included)

        json["attributes"] = self.attributes
        json["links"] = {"self": self.url(), "html": self.url("html")}

        # add relationship information
        if len(self.relationships) > 0:
            json["relationships"] = {}

        for i, items in self.relationships.items():
            json["relationships"][i] = {
                "links": {
                    "self": self.relationship_url(i, False),
                    "related": self.relationship_url(i, True),
                },
                "data": None,
            }
            if isinstance(items, list):
                json["relationships"][i]["data"] = [
                    j.toJSON("identifer")[0] for j in items
                ]
                if role != "embedded":
                    included += [j.toJSON("embedded")[0] for j in items]
            elif hasattr(items, "toJSON"):
                json["relationships"][i]["data"] = items.toJSON("identifer")[0]  # type: ignore
                if role != "embedded":
                    included.append(items.toJSON("embedded")[0])  # type: ignore

        return (json, included)

    def topJSON(self: "Controller") -> dict:
        json = self.toJSON()
        if not self.found:
            return {
                "errors": [
                    {
                        "status": HTTPStatus.NOT_FOUND,
                        "code": "not_found",
                        "title": "Code not found",
                    }
                ]
            }

        return {
            "data": json[0],
            "included": json[1],
            "links": {"self": self.url(), "html": self.url("html")},
        }

    def get_es_version(self: "Controller", es: Elasticsearch) -> list[int] | None:
        version_number = es.info().get("version").get("number")  # type: ignore
        if not version_number:
            return None
        return [int(v) for v in version_number.split(".")]


class Pagination:
    default_size: int = 10

    def __init__(self: "Pagination", page: int = 1, size: int | None = None) -> None:
        self.page = page if isinstance(page, int) else 1
        self.size = size if isinstance(size, int) else self.default_size
        self.from_ = self.get_from()
        self.pagination: dict[str, dict[str, object] | int | None] = {
            "next": None,
            "prev": None,
            "first": None,
            "last": None,
        }

    def page_query_vars(self: "Pagination", query_vars: dict = {}) -> dict:
        if self.page and self.page > 1 and "p" not in query_vars:
            query_vars["p"] = self.page
        if (
            self.size
            and self.size
            and self.size != self.default_size
            and "size" not in query_vars
        ):
            query_vars["size"] = self.size
        return query_vars

    def get_from(self: "Pagination") -> int:
        return (self.page - 1) * self.size

    def set_pages(self: "Pagination", page: int, size: int) -> None:
        self.page = page
        self.size = size

    def set_pagination(
        self: "Pagination", total_results: int, url_args: dict = {}, range: int = 5
    ) -> None:
        self.total = total_results
        self.min_page = 1
        self.max_page = math.ceil(float(total_results) / float(self.size))

        if self.size != self.default_size:
            url_args["size"] = self.size

        # next page link
        if self.page < self.max_page:
            self.pagination["next"] = {"p": self.page + 1, **url_args}

        # previous page link
        if self.page > 1:
            self.pagination["prev"] = {"p": self.page - 1, **url_args}

        # start_page link
        if (self.page - 1) > 1:
            self.pagination["first"] = {"p": self.min_page, **url_args}

        # end page link
        if (self.page + 1) < self.max_page:
            self.pagination["last"] = {"p": self.max_page, **url_args}

        self.pagination["current_page"] = self.page
        self.pagination["min_page"] = self.min_page
        self.pagination["max_page"] = self.max_page
        self.pagination["max_item"] = self.total
        self.pagination["start_item"] = self.from_ + 1
        self.pagination["end_item"] = min([self.from_ + self.size, self.total])
        # page ranges
        # @TODO calculate page ranges

    def get_meta(self: "Pagination", meta: dict) -> dict:
        meta["from"] = self.get_from()
        meta["p"] = self.page
        meta["size"] = self.size
        return meta

    def get_links(self: "Pagination", links: dict) -> dict:
        return links

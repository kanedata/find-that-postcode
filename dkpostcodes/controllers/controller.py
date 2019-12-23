import math
from urllib.parse import urlencode, urlunparse

from ..metadata import AREA_TYPES

GEOJSON_TYPES = {
    "point": "Point",  # A single geographic coordinate.
    "linestring": "LineString",  # An arbitrary line given two or more points.
    "polygon": "Polygon",  # A closed polygon whose first and last point must match, thus requiring n + 1 vertices to create an n-sided polygon and a minimum of 4 vertices.
    "multipoint": "MultiPoint",  # An array of unconnected, but likely related points.
    "multilinestring": "MultiLineString",  # An array of separate linestrings.
    "multipolygon": "MultiPolygon",  # An array of separate polygons.
    "geometrycollection": "GeometryCollection",  # A GeoJSON shape similar to the multi* shapes except that multiple types can coexist (e.g., a Point and a LineString).
}


class Controller:

    template = None
    es_index = 'geo'
    es_type = '_doc'

    def __init__(self, id, data=None):
        # main configuration
        self.urlparts = None
        self.found = False
        self.errors = []
        self.attributes = {}
        self.relationships = {}
        self.id = self.parse_id(id)
        self.pagination = None
        if data:
            self.found = True
            self.attributes = self.process_attributes(data)


    @classmethod
    def get_from_es(cls, id, es, es_config=None):
        if not es_config:
            es_config = {}
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_exclude=es_config.get("_source_exclude", []),
        )
        return cls(data.get("_id"), data.get("_source"))

    def process_attributes(self, data):
        return data

    @staticmethod
    def parse_id(id):
        return id

    def url(self, filetype=None, query_vars={}):
        path = [self.url_slug, self.id.replace(" ", "+") + self.set_url_filetype(filetype)]
        return urlunparse([
            self.urlparts.scheme if self.urlparts else "",
            self.urlparts.netloc if self.urlparts else "",
            "/".join(path),
            "",
            self.get_query_string(query_vars),
            ""
        ])

    def relationship_url(self, relationship, related=True, filetype=None, query_vars={}):
        if related:
            path = [self.url_slug, self.id.replace(" ", "+"), relationship + self.set_url_filetype(filetype)]
        else:
            path = [self.url_slug, self.id.replace(" ", "+"), "relationships", relationship + self.set_url_filetype(filetype)]
        return urlunparse([
            self.urlparts.scheme if self.urlparts else "",
            self.urlparts.netloc if self.urlparts else "",
            "/".join(path),
            "",
            self.get_query_string(query_vars),
            ""
        ])

    def set_url_filetype(self, filetype=None):
        if filetype:
            return "." + filetype
        return ""

    def get_query_string(self, query_vars={}):
        # query_vars = self.page_query_vars(query_vars)
        return urlencode(query_vars)

    def get_errors(self):
        if not self.found:
            return [
                {
                    "status": "404",
                    "title": "resource not found",
                    "detail": "resource could not be found"
                }
            ]
        return []

    # role = top|identifier|embedded
    def toJSON(self, role="top"):
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
        json["links"] = {
            "self": self.url(),
            "html": self.url("html")
        }

        # add relationship information
        if len(self.relationships) > 0:
            json["relationships"] = {}

        for i in self.relationships:
            json["relationships"][i] = {
                "links": {
                    "self": self.relationship_url(i, False),
                    "related": self.relationship_url(i, True)
                },
                "data": None
            }
            if isinstance(self.relationships[i], list):
                json["relationships"][i]["data"] = [j.toJSON("identifer")[1] for j in self.relationships[i]]
                if role != "embedded":
                    included += [j.toJSON("embedded")[1] for j in self.relationships[i]]
            else:
                json["relationships"][i]["data"] = self.relationships[i].toJSON("identifer")[1]
                if role != "embedded":
                    included.append(self.relationships[i].toJSON("embedded")[1])

        return (json, included)

    def topJSON(self):
        json = self.toJSON()
        if not self.found:
            return {
                "errors": [
                    {
                        "status": "404",
                        "code": "not_found",
                        "title": "Code not found"
                    }
                ]
            }

        return {
            "data": json[0],
            "included": json[1],
            "links": {
                "self": self.url(),
                "html": self.url("html")
            }
        }


    def get_es_version(self, es):
        version_number = es.info().get("version").get("number")
        if not version_number:
            return None
        return [int(v) for v in version_number.split(".")]


class Pagination():

    default_size = 100

    def __init__(self):
        self.page = 1 # int(bottle.request.query.page or 1)
        self.size = self.default_size #int(bottle.request.query.size or self.default_size)
        self.from_ = self.get_from()
        self.pagination = {
            "next": None,
            "prev": None,
            "first": None,
            "last": None
        }

    def page_query_vars(self, query_vars={}):
        if self.page and self.page > 1 and "page" not in query_vars:
            query_vars["page"] = self.p
        if self.size and self.size and self.size != self.default_size and "size" not in query_vars:
            query_vars["size"] = self.size
        return query_vars

    def get_from(self):
        return (self.page - 1) * self.size

    def set_pages(self, page, size):
        self.page = page
        self.size = size

    def set_pagination(self, total_results, url_args={}, range=5):
        self.total = total_results
        self.max_page = math.ceil(float(total_results) / float(self.size))

        if self.size != self.default_size:
            url_args["size"] = self.size

        # next page link
        if self.page < self.max_page:
            url_args["page"] = self.page + 1
            self.pagination["next"] = url_args

        # previous page link
        if self.page > 1:
            url_args["page"] = self.page - 1
            self.pagination["prev"] = url_args

        # start_page link
        if (self.page - 1) > 1:
            url_args["page"] = 1
            self.pagination["first"] = url_args

        # end page link
        if (self.page + 1) < self.max_page:
            url_args["page"] = self.max_page
            self.pagination["last"] = url_args

        # page ranges
        # @TODO calculate page ranges

    def get_meta(self, meta):
        meta["from"] = self.get_from()
        meta["page"] = self.page
        meta["size"] = self.size
        return meta

    def get_links(self, links):
        return links

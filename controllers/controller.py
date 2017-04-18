from metadata import AREA_TYPES
import math
from urllib.parse import urlencode, urlunparse
import bottle

GEOJSON_TYPES = {
    "point": "Point", # A single geographic coordinate.
    "linestring": "LineString", # An arbitrary line given two or more points.
    "polygon": "Polygon", # A closed polygon whose first and last point must match, thus requiring n + 1 vertices to create an n-sided polygon and a minimum of 4 vertices.
    "multipoint": "MultiPoint", # An array of unconnected, but likely related points.
    "multilinestring": "MultiLineString", # An array of separate linestrings.
    "multipolygon": "MultiPolygon", # An array of separate polygons.
    "geometrycollection": "GeometryCollection", # A GeoJSON shape similar to the multi* shapes except that multiple types can coexist (e.g., a Point and a LineString).
}

class Controller:

    template = None

    def __init__(self, config={}):
        # main configuration
        self.config = config
        self.urlparts = bottle.request.urlparts if bottle else None
        self.found = False
        self.errors = []
        self.attributes = {}
        self.relationships = {}
        self.id = None
        self.pagination = None

    def set_from_data(self, data=None):
        if data:
            self.found = True
            self.attributes = self.process_attributes(data["_source"])
            self.id = data["_id"]
        return self

    def process_attributes(self, data):
        return data

    def parse_id(self, id):
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
        #query_vars = self.page_query_vars(query_vars)
        return urlencode(query_vars)

    # role = top|identifier|embedded
    def toJSON(self, role="top"):
        json = {}
        included = []
        status = 404

        # check if anything has been found
        if not self.found:
            json["errors"] = [
                {
                    "status": str(status),
                    "title": "resource not found",
                    "detail": "resource could not be found"
                }
            ]
            return (status, json, included)

        status = 200
        json["type"] = self.url_slug
        json["id"] = self.id
        if role=="identifer":
            return (status, json, included)

        json["attributes"] = self.attributes
        json["links"] = {
            "self": self.url(),
            "html": self.url("html")
        }

        # add relationship information
        if len(self.relationships)>0:
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
                if role!="embedded":
                    included += [j.toJSON("embedded")[1] for j in self.relationships[i]]
            else:
                json["relationships"][i]["data"] = self.relationships[i].toJSON("identifer")[1]
                if role!="embedded":
                    included.append(self.relationships[i].toJSON("embedded")[1])

        return (status, json, included)

    def topJSON(self):
        json = self.toJSON()
        if not self.found:
            return (404, {
                "errors": [
                    {
                        "status": "404",
                        "code": "not_found",
                        "title": "Code not found"
                    }
                ]
            })

        return (200, {
                "data": json[1],
                "included": json[2],
                "links": {
                    "self": self.url(),
                    "html": self.url("html")
                }
            })

class Pagination():

    default_size = 100

    def __init__(self):
        self.page = int(bottle.request.query.page or 1)
        self.size = int(bottle.request.query.size or self.default_size)
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
        if self.size and self.size and self.size!=self.default_size and "size" not in query_vars:
            query_vars["size"] = self.size
        return query_vars

    def get_from(self):
        return (self.page-1) * self.size

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

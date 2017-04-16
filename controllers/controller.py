from metadata import AREA_TYPES
import math
from urllib.parse import urlencode

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
    default_size = 100

    def __init__(self, es, es_index):
        self.es_index = es_index
        self.es = es
        self.found = False
        self.data = {}
        self.id = None
        self.use_pagination = False
        self.p = None
        self.size = self.default_size
        self.pagination = {
            "next": None,
            "prev": None,
            "first": None,
            "last": None
        }
        self.areatypes = {i[0]:i for i in AREA_TYPES}

    def get_area_type(self, areatype):
        return self.areatypes.get(areatype, [])

    def url(self, filetype=None, query_vars={}):
        return "/{}/{}{}{}".format(self.url_slug, self.id, self.set_url_filetype(filetype), self.get_query_string(query_vars))

    def relationship_url(self, relationship, related=True, filetype=None, query_vars={}):
        if related:
            return "/{}/{}/{}{}{}".format(self.url_slug, self.id, relationship, self.set_url_filetype(filetype), self.get_query_string(query_vars))
        else:
            return "/{}/{}/relationships/{}{}{}".format(self.url_slug, self.id, relationship, self.set_url_filetype(filetype), self.get_query_string(query_vars))

    def template_name(self):
        if self.template:
            return self.template
        return '{}.html'.format(self.es_type)

    def set_url_filetype(self, filetype=None):
        if filetype:
            return "." + filetype
        return ""

    def get_query_string(self, query_vars={}):
        query_vars = self.page_query_vars(query_vars)
        return ('?' + urlencode(query_vars)) if len(query_vars)>0 else ''

    def page_query_vars(self, query_vars={}):
        if self.p and self.p > 1 and "page" not in query_vars:
            query_vars["page"] = self.p
        if self.size and self.size and self.size!=self.default_size and "size" not in query_vars:
            query_vars["size"] = self.size
        return query_vars


    def get_from(self):
        return (self.p-1) * self.size

    def set_pages(self, p, size):
        self.p = p
        self.size = size

    def set_pagination(self, total_results, filetype="json", url_args={}, range=5):
        self.total = total_results
        self.max_page = math.ceil(float(total_results) / float(self.size))

        if self.size != self.default_size:
            url_args["size"] = self.size

        # next page link
        if self.p < self.max_page:
            url_args["p"] = self.p + 1
            self.pagination["next"] = self.url(filetype, url_args)

        # previous page link
        if self.p > 1:
            url_args["p"] = self.p - 1
            self.pagination["prev"] = self.url(filetype, url_args)

        # start_page link
        if (self.p - 1) > 1:
            url_args["p"] = 1
            self.pagination["first"] = self.url(filetype, url_args)

        # end page link
        if (self.p + 1) < self.max_page:
            url_args["p"] = self.max_page
            self.pagination["last"] = self.url(filetype, url_args)

        # page ranges
        # @TODO calculate page ranges

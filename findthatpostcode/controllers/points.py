from urllib.parse import urlunparse

from . import postcodes
from .controller import Controller


class Point(Controller):

    es_index = "geo_postcode"
    url_slug = "points"
    template = "postcode.html.j2"
    max_distance = 10000

    def __init__(self, id, data=None, nearest_postcode=None):
        super().__init__(id, data)
        if nearest_postcode:
            self.relationships["nearest_postcode"] = nearest_postcode

    def __repr__(self):
        return "<Point {}, {}>".format(self.id[0], self.id[1])

    @staticmethod
    def get_nearest_postcodes_query(lat, lon):
        return {
            "query": {"bool": {"must_not": {"exists": {"field": "doterm"}}}},
            "sort": [
                {"_geo_distance": {"location": {"lat": lat, "lon": lon}, "unit": "m"}}
            ],
        }

    @classmethod
    def get_from_es(cls, id, es, es_config=None):
        if not es_config:
            es_config = {}

        query = cls.get_nearest_postcodes_query(id[0], id[1])

        data = es.search(
            index=es_config.get("es_index", cls.es_index),
            body=query,
            ignore=[404],
            size=1,
            _source_excludes=es_config.get("_source_exclude", []),
        )

        if data["hits"]["total"] == 0:
            return cls(id)

        postcode = data["hits"]["hits"][0]
        return cls(
            id,
            data={"distance_from_postcode": postcode["sort"][0]},
            nearest_postcode=postcodes.Postcode.get_from_es(postcode["_id"], es),
        )

    def get_by_id(self, lat, lon):
        self.set_from_data(
            {"_id": "{},{}".format(lat, lon), "_source": {"lat": lat, "lon": lon}}
        )
        query = self.get_nearest_postcodes_query(lat, lon)
        result = self.es.search(
            index=self.config.get("es_index", "postcode"), body=query, size=1
        )
        if result["hits"]["total"] > 0:
            postcode = result["hits"]["hits"][0]
            self.relationships["nearest_postcode"] = postcodes.Postcode(
                self.config
            ).set_from_data(postcode)
            self.attributes["distance_from_postcode"] = postcode["sort"][0]

    def get_errors(self):
        if self.attributes.get("distance_from_postcode") > self.max_distance:
            self.found = False
            return [
                {
                    "status": "400",
                    "code": "point_outside_uk",
                    "title": "Nearest postcode is more than 10km away",
                    "detail": "Nearest postcode ({}) is more than 10km away ({:,.1f}km). Are you sure this point is in the UK?".format(
                        self.relationships["nearest_postcode"].id,
                        (self.attributes.get("distance_from_postcode") / 1000),
                    ),
                }
            ]
        if not self.found:
            return [
                {
                    "status": "404",
                    "title": "resource not found",
                    "detail": "resource could not be found",
                }
            ]
        return []

    def topJSON(self):

        # check if postcode is too far away
        if self.attributes.get("distance_from_postcode") > self.max_distance:
            self.found = False
            return {
                "errors": [
                    {
                        "status": "400",
                        "code": "point_outside_uk",
                        "title": "Nearest postcode is more than 10km away",
                        "detail": "Nearest postcode ({}) is more than 10km away ({:,.1f}km). Are you sure this point is in the UK?".format(
                            self.relationships["nearest_postcode"].id,
                            (self.attributes.get("distance_from_postcode") / 1000),
                        ),
                    }
                ]
            }

        json = super().topJSON()
        postcode_json = self.relationships["nearest_postcode"].toJSON()
        json["included"] += postcode_json[1]
        return json

    def url(self, filetype=None, query_vars={}):
        path = [
            self.url_slug,
            "{},{}".format(*self.id) + self.set_url_filetype(filetype),
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
        self, relationship, related=True, filetype=None, query_vars={}
    ):
        if related:
            path = [
                self.url_slug,
                "{},{}".format(*self.id),
                relationship + self.set_url_filetype(filetype),
            ]
        else:
            path = [
                self.url_slug,
                "{},{}".format(*self.id),
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

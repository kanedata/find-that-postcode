from urllib.parse import urlunparse

from elasticsearch import Elasticsearch

from findthatpostcode.controllers.controller import Controller
from findthatpostcode.controllers.postcodes import Postcode
from findthatpostcode.settings import MAX_DISTANCE_FROM_POINT, POSTCODE_INDEX
from findthatpostcode.utils import ESConfig


class Point(Controller):
    es_index = POSTCODE_INDEX
    url_slug = "points"
    template = "postcode.html.j2"
    max_distance = MAX_DISTANCE_FROM_POINT

    def __init__(
        self,
        id: tuple[float, float],
        data: dict | None = None,
        nearest_postcode: Postcode | None = None,
    ):
        super().__init__(id, data)
        if nearest_postcode:
            self.relationships["nearest_postcode"] = nearest_postcode

    @staticmethod
    def parse_id(id: str | tuple[float, float]) -> tuple[float, float]:
        if isinstance(id, tuple):
            return id
        raise ValueError("ID must be a tuple of (lat, lon)")

    def __repr__(self):
        return "<Point {}, {}>".format(self.id[0], self.id[1])

    @staticmethod
    def get_nearest_postcodes_query(lat: float, lon: float) -> dict:
        return {
            "query": {"bool": {"must_not": {"exists": {"field": "doterm"}}}},
            "sort": [
                {"_geo_distance": {"location": {"lat": lat, "lon": lon}, "unit": "m"}}
            ],
        }

    @classmethod
    def get_from_es(
        cls: type["Point"],
        id: str | tuple[float, float],
        es: Elasticsearch,
        es_config: ESConfig | None = None,
    ):
        if not es_config:
            es_config = ESConfig(es_index=cls.es_index, es_type=cls.es_type)

        if not isinstance(id, tuple):
            raise ValueError("ID must be a tuple of (lat, lon)")

        query = cls.get_nearest_postcodes_query(id[0], id[1])

        data = es.search(
            index=es_config.es_index,
            body=query,
            ignore=[404],  # type: ignore
            size=1,  # type: ignore
            _source_excludes=es_config._source_exclude,  # type: ignore
        )

        if data["hits"]["total"] == 0:
            return cls(id)

        postcode = data["hits"]["hits"][0]
        return cls(
            id,
            data={"distance_from_postcode": postcode["sort"][0]},
            nearest_postcode=Postcode.get_from_es(postcode["_id"], es),
        )

    def get_errors(self) -> list[dict]:
        distance_from_postcode = self.attributes.get("distance_from_postcode")
        if not isinstance(distance_from_postcode, (int, float)):
            distance_from_postcode = 0

        nearest_postcode = self.relationships.get("nearest_postcode")
        if not isinstance(nearest_postcode, Postcode):
            return [
                {
                    "status": "400",
                    "code": "no_postcode_found",
                    "title": "No nearest postcode found",
                }
            ]

        if distance_from_postcode > self.max_distance:
            self.found = False
            return [
                {
                    "status": "400",
                    "code": "point_outside_uk",
                    "title": "Nearest postcode is more than 10km away",
                    "detail": (
                        "Nearest postcode ({}) is more than 10km away ({:,.1f}km). "
                        "Are you sure this point is in the UK?"
                    ).format(
                        nearest_postcode.id,
                        (distance_from_postcode / 1000),
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

    def topJSON(self: "Point") -> dict:
        distance_from_postcode = self.attributes.get("distance_from_postcode")
        if not isinstance(distance_from_postcode, (int, float)):
            distance_from_postcode = 0

        nearest_postcode = self.relationships.get("nearest_postcode")
        if not isinstance(nearest_postcode, Postcode):
            return {
                "errors": [
                    {
                        "status": "400",
                        "code": "no_postcode_found",
                        "title": "No nearest postcode found",
                    }
                ]
            }

        # check if postcode is too far away
        if distance_from_postcode > self.max_distance:
            self.found = False
            return {
                "errors": [
                    {
                        "status": "400",
                        "code": "point_outside_uk",
                        "title": "Nearest postcode is more than 10km away",
                        "detail": (
                            "Nearest postcode ({}) is more than 10km away ({:,.1f}km). "
                            "Are you sure this point is in the UK?"
                        ).format(
                            nearest_postcode.id,
                            (distance_from_postcode / 1000),
                        ),
                    }
                ]
            }

        json = super().topJSON()
        postcode_json = nearest_postcode.toJSON()
        json["included"] += postcode_json[1]
        return json

    def url(
        self: "Point", filetype: str | None = None, query_vars: dict | None = None
    ) -> str:
        if query_vars is None:
            query_vars = {}
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

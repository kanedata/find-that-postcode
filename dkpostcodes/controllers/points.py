from datetime import datetime
import bottle

from .controller import *
from . import postcodes


class Point(Controller):

    es_index = 'geo_postcode'
    url_slug = 'points'
    template = 'postcode.html'
    max_distance = 10000

    def __init__(self, id, data=None, nearest_postcode=None):
        super().__init__(id, data)
        if nearest_postcode:
            self.relationships["nearest_postcode"] = nearest_postcode

    def __repr__(self):
        return '<Point {}, {}>'.format(self.id[0], self.id[1])
        
    @classmethod
    def get_from_es(cls, id, es, es_config=None):
        if not es_config:
            es_config = {}

        query = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": id[0],
                            "lon": id[1]
                        },
                        "unit": "m"
                    }
                }
            ]
        }

        data = es.search(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            body=query,
            ignore=[404],
            size=1,
            _source_exclude=es_config.get("_source_exclude", []),
        )

        if data["hits"]["total"] == 0:
            return cls(id)

        postcode = data["hits"]["hits"][0]
        print(postcode)
        return cls(
            id,
            data={"distance_from_postcode": postcode["sort"][0]},
            nearest_postcode=postcodes.Postcode.get_from_es(postcode["_id"], es)
        )

    def get_by_id(self, lat, lon):
        self.set_from_data({
            "_id": "{},{}".format(lat, lon),
            "_source": {
                "lat": lat,
                "lon": lon
            }
        })
        query = {
            "query": {
                "match_all": {}
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": lat,
                            "lon": lon
                        },
                        "unit": "m"
                    }
                }
            ]
        }
        result = self.es.search(index=self.config.get("es_index", "postcode"), doc_type='postcode', body=query, size=1)
        if result["hits"]["total"] > 0:
            postcode = result["hits"]["hits"][0]
            self.relationships["nearest_postcode"] = controllers.postcodes.Postcode(self.config).set_from_data(postcode)
            self.attributes["distance_from_postcode"] = postcode["sort"][0]

    def topJSON(self):

        # check if postcode is too far away
        if self.attributes.get("distance_from_postcode") > self.max_distance:
            return (400, {
                "errors": [{
                    "status": "400",
                    "code": "point_outside_uk",
                    "title": "Nearest postcode is more than 10km away",
                    "detail": "Nearest postcode ({}) is more than 10km away ({:,.1f}km). Are you sure this point is in the UK?".format(self.postcode.id, (self.attributes.get("distance_from_postcode") / 1000))
                }]
            })

        json = super().topJSON()
        postcode_json = self.relationships["nearest_postcode"].toJSON()
        json[1]["included"] += postcode_json[2]
        return json

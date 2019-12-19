from datetime import datetime
import bottle

from .controller import *
from . import postcodes


class Point(Controller):

    es_type = 'postcode'
    url_slug = 'points'
    template = 'postcode.html'
    max_distance = 10000

    def __init__(self, config):
        super().__init__(config)

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
        result = self.config.get("es").search(index=self.config.get("es_index", "postcode"), doc_type='postcode', body=query, size=1)
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

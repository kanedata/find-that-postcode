from datetime import datetime
import bottle

from .controller import *
import controllers.postcodes

class Point(Controller):

    es_type = 'postcode'
    url_slug = 'points'
    template = 'postcode.html'
    max_distance = 10000

    def __init__(self, config):
        super().__init__(config)

    def get_by_id(self, lat, lon):
        self.set_from_data({
            "_id": "{},{}".format(lat,lon),
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
        if result["hits"]["total"]>0:
            postcode = result["hits"]["hits"][0]
            self.relationships["nearest_postcode"] = controllers.postcodes.Postcode(self.config).set_from_data(postcode)
            self.attributes["distance_from_postcode"] = postcode["sort"][0]

    def return_result(self, filetype):
        json = self.toJSON()
        if not self.found:
            return bottle.abort(404)

        # check if postcode is too far away
        if self.attributes.get("distance_from_postcode") > self.max_distance:
            return {
                "errors": [{
                    "status": "400",
                    "code": "point_outside_uk",
                    "title": "Nearest postcode ({}) is more than 10km away ({:,.1f}km). Are you sure this point is in the UK?".format( self.postcode.id, (self.attributes.get("distance_from_postcode") / 1000) )
                }]
            }

        if filetype=="html":

            return bottle.template('postcode.html',
                result=self.postcode.attributes,
                postcode=self.postcode.id,
                point={"lat": self.attributes.get("lat"), "lon": self.attributes.get("lon"), "distance": self.attributes.get("distance_from_postcode")},
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {
                "data": json[1],
                "included": json[2],
                "links": {
                    "self": self.url(),
                    "html": self.url("html")
                }
            }

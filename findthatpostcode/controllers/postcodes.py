from datetime import datetime
import bottle
import re

from ..metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES, OAC11_CODE, RU11IND_CODES
from .controller import *
from . import areas
from . import places
from . import areatypes


class Postcode(Controller):

    es_index = 'geo_postcode'
    url_slug = 'postcodes'
    date_fields = ["dointr", "doterm"]
    not_area_fields = ["osgrdind", "usertype"]

    def __init__(self, id, data=None, pcareas=None, places=None):
        super().__init__(id, data)
        if pcareas:
            self.relationships["areas"] = pcareas
            self.relationships["nearest_places"] = places

    def __repr__(self):
        return '<Postcode {}>'.format(self.id)


    @classmethod
    def get_from_es(cls, id, es, es_config=None):
        if not es_config:
            es_config = {}
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_excludes=es_config.get("_source_exclude", []),
        )

        if not data.get("found"):
            return cls(id)
        
        pcareas = []
        postcode = data.get("_source")
        for k in list(postcode.keys()):
            if isinstance(postcode[k], str) and re.match(r'[A-Z][0-9]{8}', postcode[k]):
                area = areas.Area.get_from_es(postcode[k], es, examples_count=0) 
                if area.found:
                    postcode[k + "_name"] = area.attributes.get("name")
                    pcareas.append(area)

        places = cls.get_nearest_places(data.get("_source", {}).get("location"), es, 10)
        return cls(data.get("_id"), data.get("_source"), pcareas, places)
    
    def process_attributes(self, postcode):

        # turn dates into dates
        for i in self.date_fields:
            if postcode.get(i) and not isinstance(postcode[i], datetime):
                try:
                    postcode[i] = datetime.strptime(postcode[i][0:10], "%Y-%m-%d")
                except ValueError:
                    continue
        
        if OAC11_CODE.get(postcode.get("oac11")):
            postcode["oac11"] = {
                "code": postcode["oac11"],
                "supergroup": OAC11_CODE.get(postcode["oac11"])[0],
                "group": OAC11_CODE.get(postcode["oac11"])[1],
                "subgroup": OAC11_CODE.get(postcode["oac11"])[2],
            }

        if RU11IND_CODES.get(postcode.get("ru11ind")):
            postcode["ru11ind"] = {
                "code": postcode["ru11ind"],
                "description": RU11IND_CODES.get(postcode["ru11ind"]),
            }

        return postcode

    @staticmethod
    def get_nearest_places(location, es, examples_count=10):
        if not location:
            return []
        query = {
            "query": {
                "match": {
                    "descnm": {"query": "LOC"}
                }
            },
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": location.get("lat"),
                            "lon": location.get("lon")
                        },
                        "unit": "m"
                    }
                }
            ]
        }
        example = es.search(index='geo_placename', body=query, size=examples_count)
        return [places.Place(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    def get_attribute(self, attr):
        """
        Get an attribute or area by the field name

        Adding "_name" to end of the code will return the name rather than code
        """
        if attr in self.attributes:
            return self.attributes.get(attr)

        for a in self.relationships["areas"]:
            if attr.endswith("_name"):
                if a.relationships["areatype"].id == attr[:-5]:
                    return a.attributes.get("name")
            else:
                if a.relationships["areatype"].id == attr:
                    return a.id


    def get_area(self, areatype):
        """
        Get the area for this postcode based on the type
        """
        for a in self.relationships["areas"]:
            if a.relationships["areatype"].id == areatype:
                return a


    @staticmethod
    def parse_id(postcode):
        """
        standardises a postcode into the correct format
        """

        if postcode is None:
            return None

        # check for blank/empty
        # put in all caps
        postcode = postcode.strip().upper()
        if postcode == '':
            return None

        # replace any non alphanumeric characters
        postcode = re.sub('[^0-9a-zA-Z]+', '', postcode)

        # check for nonstandard codes
        if len(postcode) > 7:
            return postcode

        first_part = postcode[:-3].strip()
        last_part = postcode[-3:].strip()

        # check for incorrect characters
        first_part = list(first_part)
        last_part = list(last_part)
        if last_part[0] == "O":
            last_part[0] = "0"

        return "%s %s" % ("".join(first_part), "".join(last_part))

    def toJSON(self, role="top"):
        json = super().toJSON(role)
        for i in self.date_fields:
            if json[0].get("attributes", {}).get(i) and isinstance(json[0]["attributes"][i], datetime):
                json[0]["attributes"][i] = json[0]["attributes"][i].strftime("%Y-%m-%d")

        return json

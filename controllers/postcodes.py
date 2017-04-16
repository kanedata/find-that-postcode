from datetime import datetime
import bottle

from metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES

from .controller import Controller
from .areatypes import Areatype
from .areas import get_area_object

class Postcode(Controller):

    es_type = 'postcode'
    url_slug = 'postcodes'
    date_fields = ["dointr", "doterm"]
    template = 'postcode.html'

    def __init__(self, es, es_index):
        super().__init__(es, es_index)

    def get(self, postcode):
        postcode = postcode.replace("+", "")
        postcode = self.parse_postcode(postcode)
        result = self.es.get(index=self.es_index, doc_type=self.es_type, id=postcode, ignore=[404])
        if result["found"]:
            self.found = True
            self.data = self.process_result(result["_source"])
            self.id = result["_id"]

    def jsonapi(self):
        for i in self.date_fields:
            if self.data[i]:
                self.data[i] = self.data[i].strftime("%Y%m")

        return {
            "type": "postcodes",
            "id": self.id,
            "attributes": self.data,
            "relationships": {
                "areas": {
                    "data": [{
                        "type": "areas",
                        "id": self.data[a[0]]["id"]
                    } for a in AREA_TYPES if a[0] in self.data],
                    "links": {
                        "self": self.relationship_url("areas", False),
                        "related": self.relationship_url("areas", True)
                    }
                }
            }
        }

    def jsonapi_included(self):
        areas = [self.data[a[0]] for a in AREA_TYPES if a[0] in self.data]
        return [self.get_area_object({
            "_id": a["id"],
            "_source": a
        }) for a in areas]

    def process_result(self, postcode):
        for i in postcode:
            if postcode[i]:
                code = self.es.get(index=self.es_index, doc_type='code', id=postcode[i], ignore=[404], _source_exclude=["boundary"])
                if i in ["osgrdind", "usertype"]:
                    pass
                elif code["found"]:
                    code["_source"]["id"] = code["_id"]
                    postcode[i] = code["_source"]
                    if code["_id"].endswith("99999999"):
                        postcode[i]["name"] = ""
                elif i in ["wz11", "oa11"]:
                    postcode[i] = {
                        "id": postcode[i],
                        "name": postcode[i],
                        "type": i,
                        "typename": self.get_area_type(i)[2]
                    }

        # sort out leps @TODO do this properly
        postcode["lep"] = postcode["lep1"]

        # turn dates into dates
        for i in self.date_fields:
            if postcode[i]:
                postcode[i] = datetime.strptime(postcode[i], "%Y-%m-%dT%H:%M:%S")

        return postcode


    def parse_postcode(self, postcode):
        """
        standardises a postcode into the correct format
        """

        if postcode is None:
            return None

        # check for blank/empty
        postcode = postcode.strip()
        if postcode=='':
            return None

        # check for nonstandard codes
        if len(postcode.replace(" ", ""))>7:
            return postcode

        first_part = postcode[:-3].strip()
        last_part = postcode[-3:].strip()

        # check for incorrect characters
        first_part = list(first_part)
        last_part = list(last_part)
        if last_part[0]=="O":
            last_part[0] = "0"

        return "%s %s" % ("".join(first_part), "".join(last_part) )

    def return_result(self, filetype):
        if not self.found:
            return bottle.abort(404)

        if filetype=="html":
            return bottle.template(self.template_name(),
                result=self.data,
                postcode=self.id,
                point=None,
                area_types=AREA_TYPES,
                key_area_types=KEY_AREA_TYPES,
                other_codes=OTHER_CODES
                )
        elif filetype=="json":
            return {
                "data": self.jsonapi(),
                "included": self.jsonapi_included(),
                "links": {"self": self.url()}
            }

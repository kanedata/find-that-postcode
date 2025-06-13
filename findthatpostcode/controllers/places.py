import re

from findthatpostcode.controllers.controller import Controller


class Place(Controller):
    es_index = "geo_placename"
    url_slug = "places"
    template = "place.html.j2"

    def __init__(self, id, data=None, **kwargs):
        super().__init__(id)
        self.relationships["nearest_postcodes"] = kwargs.get("nearest_postcodes")
        self.relationships["nearest_places"] = kwargs.get("nearest_places")
        self.relationships["areas"] = kwargs.get("areas")
        if data:
            self.found = True
            self.attributes = self.process_attributes(data)

    def __repr__(self):
        return "<Place {}>".format(self.id)

    @classmethod
    def get_from_es(cls, id, es, es_config=None, examples_count=5, recursive=True):
        from findthatpostcode.controllers.areas import Area

        if not es_config:
            es_config = {}

        # fetch the initial area
        data = es.get(
            index=es_config.get("es_index", cls.es_index),
            doc_type=es_config.get("es_type", cls.es_type),
            id=cls.parse_id(id),
            ignore=[404],
            _source_excludes=[],
        )
        relationships = {
            "nearest_postcodes": [],
            "nearest_places": [],
            "areas": [],
        }
        for k, v in data.get("_source", {}).get("areas", {}).items():
            if isinstance(v, str) and re.match(r"[A-Z][0-9]{8}", v):
                area = Area.get_from_es(v, es, examples_count=0)
                if area.found:
                    # data["_source"]["areas"][k + "_name"] =
                    # area.attributes.get("name")
                    relationships["areas"].append(area)

        if examples_count:
            relationships["nearest_postcodes"] = cls.get_nearest_postcodes(
                data.get("_source", {}).get("location"),
                es,
                examples_count=examples_count,
            )
            relationships["nearest_places"] = cls.get_nearest_places(
                data.get("_source", {}).get("location"), es, examples_count=10
            )

        return cls(data.get("_id"), data=data.get("_source"), **relationships)

    def process_attributes(self, data):
        if "name" not in data:
            for k in data.keys():
                if k.startswith("place") and k.endswith("nm"):
                    data["name"] = data[k]
                    del data[k]
                    break
        return data

    @staticmethod
    def get_nearest_postcodes(location, es, examples_count=5):
        from findthatpostcode.controllers.postcodes import Postcode

        if not location:
            return []
        query = {
            "query": {"match_all": {}},
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": location.get("lat"),
                            "lon": location.get("lon"),
                        },
                        "unit": "m",
                    }
                }
            ],
        }
        example = es.search(index="geo_postcode", body=query, size=examples_count)
        return [Postcode(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    @staticmethod
    def get_nearest_places(location, es, examples_count=10):
        if not location:
            return []
        query = {
            "query": {"match": {"descnm": {"query": "LOC"}}},
            "sort": [
                {
                    "_geo_distance": {
                        "location": {
                            "lat": location.get("lat"),
                            "lon": location.get("lon"),
                        },
                        "unit": "m",
                    }
                }
            ],
        }
        example = es.search(index="geo_placename", body=query, size=examples_count)
        return [Place(e["_id"], e["_source"]) for e in example["hits"]["hits"]]

    def get_area(self, areatype):
        """
        Get the area for this postcode based on the type
        """
        for a in self.relationships["areas"]:
            if a.relationships["areatype"].id == areatype:
                return a

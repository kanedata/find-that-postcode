from flask import Blueprint, current_app

from .utils import return_result
# from dkpostcodes.controllers.areas import Area
from dkpostcodes.db import get_db

bp = Blueprint('areas', __name__, url_prefix='/areas')

@bp.route('/<areacode>')
@bp.route('/<areacode>.<filetype>')
def get_area(areacode, filetype="json"):
    # a = Area(current_app.config, get_db())
    # examples_count = 5 if filetype == "html" else 5
    # a.get_by_id(areacode.strip(), examples_count=examples_count)
    # (status, result) = a.topJSON()
    # print(result)
    # return return_result(result, status, filetype, "area.html")

    es = get_db()
    
    result = Area.get_from_es(areacode, es)
    return {
        "data": result.data,
        "entity": result.entity,
        "example_postcodes": result.example_postcodes,
    }


class Area:

    es_index = "geo_area"
    es_type = "_doc"

    def __init__(self, id, data, entity=None, example_postcodes=[]):
        self.id = id
        self.data = data
        self.entity = entity
        self.example_postcodes = example_postcodes

    @classmethod
    def get_from_es(cls, id, es, es_index="geo_area", es_type="_doc", _source_exclude=["boundary"]):
        data = es.get(index=es_index, doc_type=es_type, id=id, ignore=[404], _source_exclude=_source_exclude)
        entity = {}
        if data["found"]:
            entity = es.get(index="geo_entity", doc_type="_doc", id=data["_source"].get("entity"))

        postcodes = cls.get_example_postcodes(id, es)

        return cls(id, data.get("_source"), entity.get("_source"), postcodes)
    
    @staticmethod
    def get_example_postcodes(id, es, examples_count=5):
        query = {
            "query": {
                "function_score": {
                    "query": {
                        "query_string": {
                            "query": id
                        }
                    },
                    "random_score": {}
                }

            }
        }
        example = es.search(index='geo_postcode', doc_type='_doc', body=query, size=examples_count)
        return [e for e in example["hits"]["hits"]]

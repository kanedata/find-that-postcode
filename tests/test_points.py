import server
import bottle
import pytest
from elasticsearch import Elasticsearch

app = bottle.default_app()
app.config["es"] = Elasticsearch()
app.config["es_index"] = "postcode"


def test_point_json():
    point_json = server.get_point(51.501,-0.2936)

    assert point_json.get("data",{}).get("relationships",{}).get("nearest_postcode",{}).get("data",{}).get("id") == "W5 4NH"

    assert point_json.get("data",{}).get("attributes",{}).get("distance_from_postcode") == 68.9707515287199

def test_point_json_distance():
    pass

def test_point_html():
    pass

def test_point_html_distance():
    pass

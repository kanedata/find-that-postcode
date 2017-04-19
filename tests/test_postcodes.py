import server
import bottle
import pytest
from elasticsearch import Elasticsearch

app = bottle.default_app()
app.config["es"] = Elasticsearch()
app.config["es_index"] = "postcode"

def test_postcode_json():
    postcode_json = server.postcode("SW1A 1AA")
    areas = postcode_json.get("data", {}).get("relationships", {}).get("areas", {}).get("data", [])
    area_codes = [a["id"] for a in areas]
    assert "E35000546" in area_codes

    included_area_codes = [a["id"] for a in postcode_json.get("included", [])]
    assert "E35000546" in included_area_codes

    assert postcode_json.get("data", {}).get("attributes", {}).get("lat") == 51.501009
    assert postcode_json.get("data", {}).get("attributes", {}).get("long") == -0.141588

def test_missing_postcode_json():
    with pytest.raises(bottle.HTTPError):
        postcode_json = server.postcode("1234567")

def test_postcode_html():
    pass

def test_postcode_missing_html():
    pass

def test_postcode_redirect():
    pass

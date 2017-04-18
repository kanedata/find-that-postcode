import server
import bottle
import pytest
from elasticsearch import Elasticsearch

app = bottle.default_app()
app.config["es"] = Elasticsearch()
app.config["es_index"] = "postcode"

def test_areatype_json():
    areatypes_json = server.areatype("cty")

    assert areatypes_json.get("data", {}).get("attributes", {}).get("full_name") == "County"

    assert len(areatypes_json.get("included", []))==28

def test_areatype_json_missing():
    pass

def test_areatype_html():
    pass

def test_areatype_html_missing():
    pass

def test_areatypes_json():
    pass

def test_areatypes_html():
    pass

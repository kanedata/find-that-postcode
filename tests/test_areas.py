import server
import bottle
import pytest
from elasticsearch import Elasticsearch

app = bottle.default_app()
app.config["es"] = Elasticsearch()
app.config["es_index"] = "postcode"


def test_area_json():
    area_code = "E35000546"
    area_json = server.area(area_code)

    assert area_json.get("data", {}).get("attributes", {}).get("name") == "City of Westminster BUASD"

    assert len(area_json.get("data", {}).get("relationships", {}).get("example_postcodes", {}).get("data")) == 5

    for i in area_json.get("included", []):
        if i.get("type") == "postcodes":
            assert area_code in [a["id"] for a in i.get("relationships", {}).get("areas", {}).get("data", [])]


def test_missing_area_json():
    with pytest.raises(bottle.HTTPError):
        server.area("1234567")


def test_area_html():
    pass


def test_area_missing_html():
    pass


def test_area_geojson():
    pass


def test_area_search():
    pass


def test_area_search_nonsense():
    pass


def test_area_search_blank():
    pass

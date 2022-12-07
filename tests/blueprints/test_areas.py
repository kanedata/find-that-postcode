import html

from tests.fixtures import client

AREA_CODE = "S02000783"
AREA_NAME = "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"


def test_area_json(client):
    rv = client.get("/areas/{}.json".format(AREA_CODE))
    data = rv.get_json()

    assert rv.mimetype == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"

    assert data.get("data", {}).get("attributes", {}).get("name") == AREA_NAME
    assert (
        len(
            data.get("data", {})
            .get("relationships", {})
            .get("example_postcodes", {})
            .get("data")
        )
        == 5
    )


def test_missing_area_json(client):
    rv = client.get("/areas/123445676.json")
    assert rv.status == "404 NOT FOUND"


def test_area_html(client):
    rv = client.get("/areas/{}.html".format(AREA_CODE))
    content = rv.data.decode("utf8")
    assert rv.mimetype == "text/html"
    assert AREA_NAME in content
    assert AREA_CODE in content


def test_area_missing_html(client):
    rv = client.get("/areas/123445676.html")
    content = rv.data.decode("utf8").lower()
    assert rv.mimetype == "text/html"
    assert "not found" in content


def test_area_geojson(client):
    rv = client.get("/areas/{}.geojson".format(AREA_CODE))
    data = rv.get_json()

    assert rv.mimetype == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert data.get("type") == "FeatureCollection"
    assert len(data.get("features")) == 1
    assert data.get("features")[0].get("type") == "Feature"
    assert len(data["features"][0]["geometry"]["coordinates"][0]) > 3
    assert len(data["features"][0]["properties"]) > 0
    assert data["features"][0]["properties"]["name"] == AREA_NAME


def test_area_search(client):
    rv = client.get("/areas/search")
    assert rv.headers["Location"] == "/search/"
    assert rv.status_code == 301


def test_area_names(client):
    rv = client.get("/areas/names.csv")
    content = rv.data.decode("utf8")
    assert rv.mimetype == "text/csv"
    assert "E01020135" in content

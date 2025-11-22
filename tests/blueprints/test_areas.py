from http import HTTPStatus

import pytest

AREA_CODE = "S02000783"
AREA_NAME = "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/areas/{}".format(AREA_CODE),
        "/areas/{}.json".format(AREA_CODE),
        "/api/v1/areas/{}".format(AREA_CODE),
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_area_json(client, endpoint, origin):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    assert rv.status_code == HTTPStatus.OK

    print(rv.headers)
    data = rv.json()

    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"

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
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/areas/{}".format("123445676"),
        "/areas/{}.json".format("123445676"),
        "/api/v1/areas/{}".format("123445676"),
    ],
)
def test_missing_area_json(client, endpoint):
    rv = client.get(endpoint)
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_area_html(client):
    rv = client.get("/areas/{}.html".format(AREA_CODE))
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert AREA_NAME in rv.text
    assert AREA_CODE in rv.text


def test_area_missing_html(client):
    rv = client.get("/areas/123445676.html")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert "not found" in rv.text.lower()


@pytest.mark.parametrize(
    "endpoint",
    [
        "/areas/{}.geojson".format(AREA_CODE),
        "/api/v1/areas/{}.geojson".format(AREA_CODE),
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_area_geojson(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    data = rv.json()

    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
    assert data.get("type") == "FeatureCollection"
    assert len(data.get("features")) == 1
    assert data.get("features")[0].get("type") == "Feature"
    assert len(data["features"][0]["geometry"]["coordinates"][0]) > 3
    assert len(data["features"][0]["properties"]) > 0
    assert data["features"][0]["properties"]["name"] == AREA_NAME
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


def test_area_search(client_redirect):
    rv = client_redirect.get("/areas/search")
    assert rv.status_code == 301
    assert rv.headers["Location"] == "http://testserver/search/"


def test_area_names(client):
    rv = client.get("/areas/names.csv")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/csv"
    assert "E01020135" in rv.text

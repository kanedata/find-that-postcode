AREA_CODE = "S02000783"
AREA_NAME = "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"


def test_area_json(client):
    rv = client.get("/areas/{}.json".format(AREA_CODE))
    print(rv.headers)
    data = rv.json()

    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
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
    assert rv.status_code == 404


def test_area_html(client):
    rv = client.get("/areas/{}.html".format(AREA_CODE))
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert AREA_NAME in rv.text
    assert AREA_CODE in rv.text


def test_area_missing_html(client):
    rv = client.get("/areas/123445676.html")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert "not found" in rv.text.lower()


def test_area_geojson(client):
    rv = client.get("/areas/{}.geojson".format(AREA_CODE))
    data = rv.json()

    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert data.get("type") == "FeatureCollection"
    assert len(data.get("features")) == 1
    assert data.get("features")[0].get("type") == "Feature"
    assert len(data["features"][0]["geometry"]["coordinates"][0]) > 3
    assert len(data["features"][0]["properties"]) > 0
    assert data["features"][0]["properties"]["name"] == AREA_NAME


def test_area_search(client):
    rv = client.get("/areas/search")
    assert rv.status_code == 301
    assert rv.headers["Location"] == "/search/"


def test_area_names(client):
    rv = client.get("/areas/names.csv")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/csv"
    assert "E01020135" in rv.text

from tests.fixtures import client

AREA_CODE = 'S02000783'
AREA_NAME = "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"

def test_area_json(client):
    rv = client.get('/areas/{}.json'.format(AREA_CODE))
    data = rv.get_json()

    assert rv.mimetype == 'application/json'

    assert data.get("data", {}).get("attributes", {}).get("name") == AREA_NAME

    assert len(data.get("data", {}).get("relationships", {}).get("example_postcodes", {}).get("data")) == 5

    for i in data.get("included", []):
        if i.get("type") == "postcodes":
            assert AREA_CODE in [a["id"] for a in i.get("relationships", {}).get("areas", {}).get("data", [])]


def test_missing_area_json(client):
    rv = client.get('/areas/123445676.json')
    assert rv.status == '404'


def test_area_html(client):
    rv = client.get('/areas/{}.html'.format(AREA_CODE))
    content = rv.data.decode("utf8")
    assert AREA_NAME in content
    assert AREA_CODE in content


def test_area_missing_html(client):
    rv = client.get('/areas/123445676.html')
    content = rv.data.decode("utf8").lower()
    assert "not found" in content


def test_area_geojson(client):
    rv = client.get('/areas/{}.geojson'.format(AREA_CODE))
    data = rv.get_json()

    assert rv.mimetype == 'application/json'
    assert data.get("type") == "FeatureCollection"
    assert len(data.get("features")) == 1
    assert data.get("features")[0].get("type") == "Feature"
    assert len(data["features"][0]["geometry"]["coordinates"]) > 3
    assert len(data["features"][0]["geometry"]["attributes"]) > 0
    assert data["features"][0]["geometry"]["attributes"]["name"] == AREA_NAME


def test_area_search(client):
    pass


def test_area_search_nonsense(client):
    pass


def test_area_search_blank(client):
    pass

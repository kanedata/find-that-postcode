from tests.fixtures import client

def test_postcode_json(client):
    rv = client.get('/postcodes/SW1A 1AA')
    postcode_json = rv.get_json()

    areas = postcode_json.get("data", {}).get("relationships", {}).get("areas", {}).get("data", [])
    area_codes = [a["id"] for a in areas]
    assert "E35000546" in area_codes

    included_area_codes = [a["id"] for a in postcode_json.get("included", [])]
    assert "E35000546" in included_area_codes

    assert postcode_json.get("data", {}).get("attributes", {}).get("lat") == 51.501009
    assert postcode_json.get("data", {}).get("attributes", {}).get("long") == -0.141588


def test_missing_postcode_json(client):
    rv = client.get('/postcodes/14214124')
    assert rv.status == '404'


def test_postcode_html(client):
    pass


def test_postcode_missing_html(client):
    pass


def test_postcode_redirect(client):
    pass

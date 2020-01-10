from tests.fixtures import client

def test_postcode_json(client):
    rv = client.get('/postcodes/EX36 4AT')
    postcode_json = rv.get_json()

    assert rv.mimetype == 'application/json'

    areas = postcode_json.get("data", {}).get("relationships", {}).get("areas", {}).get("data", [])
    area_codes = [a["id"] for a in areas]
    assert "E01020135" in area_codes

    included_area_codes = [a["id"] for a in postcode_json.get("included", [])]
    assert "E01020135" in included_area_codes

    assert postcode_json.get("data", {}).get("attributes", {}).get("lat") == 51.01467
    assert postcode_json.get("data", {}).get("attributes", {}).get("long") == -3.83317


def test_postcode_missing_json(client):
    rv = client.get('/postcodes/14214124')
    assert rv.mimetype == 'application/json'
    assert rv.status == '404 NOT FOUND'


def test_postcode_html(client):
    rv = client.get('/postcodes/EX36 4AT.html')
    assert rv.mimetype == 'text/html'
    content = rv.data.decode("utf8")
    assert 'EX36 4AT' in content
    assert 'E01020135' in content


def test_postcode_missing_html(client):
    rv = client.get('/postcodes/14214124.html')
    assert rv.status == '404 NOT FOUND'
    assert rv.mimetype == 'text/html'
    content = rv.data.decode("utf8").lower()
    assert "14214124" in content
    assert "not found" in content


def test_postcode_redirect(client):
    pass

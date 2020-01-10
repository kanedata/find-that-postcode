from tests.fixtures import client

AREATYPE_CODE = 'cty'

def test_areatype_json(client):
    rv = client.get('/areatypes/{}.json'.format(AREATYPE_CODE))
    data = rv.get_json()

    assert data.get("data", {}).get("attributes", {}).get("full_name") == "County"

    assert len(data.get("included", [])) == 28


def test_areatype_json_missing(client):
    pass


def test_areatype_html(client):
    pass


def test_areatype_html_missing(client):
    pass


def test_areatypes_json(client):
    pass


def test_areatypes_html(client):
    pass

from tests.fixtures import client

def test_point_json(client):
    rv = client.get('/points/51.501,-0.2936')
    point_json = rv.get_json()

    assert point_json.get("data", {}).get("relationships", {}).get("nearest_postcode", {}).get("data", {}).get("id") == "W5 4NH"

    assert point_json.get("data", {}).get("attributes", {}).get("distance_from_postcode") == 68.9707515287199


def test_point_json_distance(client):
    pass


def test_point_html(client):
    pass


def test_point_html_distance(client):
    pass

import pytest


@pytest.mark.parametrize(
    "endpoint",
    [
        "/points/51.501,-0.2936",
        "/points/51.501,-0.2936.json",
        "/api/v1/points/51.501,-0.2936",
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_point_json(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    point_json = rv.json()

    assert (
        point_json.get("data", {})
        .get("relationships", {})
        .get("nearest_postcode", {})
        .get("data", {})
        .get("id")
        == "EX36 4AT"
    )
    assert (
        point_json.get("data", {}).get("attributes", {}).get("distance_from_postcode")
        == 68.9707515287199
    )
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


def test_point_json_distance(client):
    pass


def test_point_html(client):
    rv = client.get("/points/51.501,-0.2936.html")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    content = rv.text
    assert "EX36 4AT" in content
    assert "E01020135" in content
    assert "E01020122" not in content
    assert "69.0" in content


def test_point_html_distance(client):
    pass

def test_point_json(client):
    rv = client.get("/points/51.501,-0.2936")
    point_json = rv.get_json()

    assert rv.headers["Access-Control-Allow-Origin"] == "*"
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


def test_point_json_distance(client):
    pass


def test_point_html(client):
    rv = client.get("/points/51.501,-0.2936.html")
    assert rv.mimetype == "text/html"
    content = rv.data.decode("utf8")
    assert "EX36 4AT" in content
    assert "E01020135" in content
    assert "E01020122" not in content
    assert "69.0" in content


def test_point_html_distance(client):
    pass

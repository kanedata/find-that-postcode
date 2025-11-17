def test_index(client):
    rv = client.get("/")
    content = rv.text
    assert rv.status_code == 200
    assert "postcode" in content
    assert "Contains OS data © Crown copyright and database right" in content
    assert (
        "Contains Royal Mail data © Royal Mail copyright and database right" in content
    )
    assert (
        "Contains National Statistics data © Crown copyright and database right"
        in content
    )


def test_about(client):
    rv = client.get("/about")
    content = rv.text
    assert rv.status_code == 200
    assert "postcode" in content
    assert "Contains OS data © Crown copyright and database right" in content
    assert (
        "Contains Royal Mail data © Royal Mail copyright and database right" in content
    )
    assert (
        "Contains National Statistics data © Crown copyright and database right"
        in content
    )


def test_tool_reduce_geojson(client):
    rv = client.get("/tools/reduce-geojson")
    assert rv.status_code == 200
    assert "geojson" in rv.text


def test_tool_merge_geojson(client):
    rv = client.get("/tools/merge-geojson")
    assert rv.status_code == 200
    assert "geojson" in rv.text

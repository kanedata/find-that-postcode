from http import HTTPStatus

from fastapi.testclient import TestClient


def test_index(client: TestClient):
    rv = client.get("/")
    content = rv.text
    assert rv.status_code == HTTPStatus.OK
    assert "postcode" in content
    assert "Contains OS data © Crown copyright and database right" in content
    assert (
        "Contains Royal Mail data © Royal Mail copyright and database right" in content
    )
    assert (
        "Contains National Statistics data © Crown copyright and database right"
        in content
    )


def test_about(client: TestClient):
    rv = client.get("/about")
    content = rv.text
    assert rv.status_code == HTTPStatus.OK
    assert "postcode" in content
    assert "Contains OS data © Crown copyright and database right" in content
    assert (
        "Contains Royal Mail data © Royal Mail copyright and database right" in content
    )
    assert (
        "Contains National Statistics data © Crown copyright and database right"
        in content
    )


def test_tool_reduce_geojson(client: TestClient):
    rv = client.get("/tools/reduce-geojson")
    assert rv.status_code == HTTPStatus.OK
    assert "geojson" in rv.text


def test_tool_merge_geojson(client: TestClient):
    rv = client.get("/tools/merge-geojson")
    assert rv.status_code == HTTPStatus.OK
    assert "geojson" in rv.text

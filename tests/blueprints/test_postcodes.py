from http import HTTPStatus

import pytest


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/EX36 4AT",
        "/postcodes/EX36 4AT.json",
        "/api/v1/postcodes/EX36 4AT",
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_postcode_json(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    postcode_json = rv.json()

    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"

    areas = (
        postcode_json.get("data", {})
        .get("relationships", {})
        .get("areas", {})
        .get("data", [])
    )
    area_codes = [a["id"] for a in areas]
    assert "E01020135" in area_codes

    included_area_codes = [a["id"] for a in postcode_json.get("included", [])]
    assert "E01020135" in included_area_codes

    assert postcode_json.get("data", {}).get("attributes", {}).get("lat") == 51.01467
    assert postcode_json.get("data", {}).get("attributes", {}).get("long") == -3.83317
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/14214124",
        "/postcodes/14214124.json",
        "/api/v1/postcodes/14214124",
    ],
)
def test_postcode_missing_json(client, endpoint):
    rv = client.get(endpoint)
    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_postcode_html(client):
    rv = client.get("/postcodes/EX36 4AT.html")
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert "EX36 4AT" in rv.text
    assert "E01020135" in rv.text
    assert "E01020122" not in rv.text


def test_postcode_missing_html(client):
    rv = client.get("/postcodes/14214124.html")
    assert rv.status_code == HTTPStatus.NOT_FOUND
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"


def test_postcode_redirect(client_redirect):
    rv = client_redirect.get("/postcodes/redirect?postcode=EX36 4AT")
    assert rv.status_code == 303
    assert rv.headers["Location"].endswith("/postcodes/EX36%204AT.html")


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/hash/abc1",
        "/postcodes/hash/abc1.json",
        "/api/v1/postcodes/hash/abc1",
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_postcode_hash(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(f"{endpoint}?properties=ward_code", headers=headers)
    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
    data = rv.json()
    assert "data" in data
    assert data["data"]
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/hash/ab",
        "/postcodes/hash/ab.json",
        "/api/v1/postcodes/hash/ab",
    ],
)
def test_postcode_hash_too_small(client, endpoint):
    rv = client.get(f"{endpoint}?properties=ward_code")
    assert rv.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/hashes",
        "/postcodes/hashes.json",
        "/api/v1/postcodes/hashes",
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_postcode_hashes(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.post(
        endpoint,
        data=dict(
            hash="abc1",
            properties=["ward_code"],
        ),
        headers=headers,
    )
    assert rv.headers["Content-Type"].split(";")[0].strip() == "application/json"
    data = rv.json()
    assert "data" in data
    assert data["data"]
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/postcodes/hashes",
        "/postcodes/hashes.json",
        "/api/v1/postcodes/hashes",
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_postcode_hashes_too_small(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.post(
        endpoint,
        data=dict(
            hash="ab",
            properties=["ward_code"],
        ),
        headers=headers,
    )
    assert rv.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"

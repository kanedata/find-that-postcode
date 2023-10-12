

def test_postcode_json(client):
    rv = client.get("/postcodes/EX36 4AT")
    postcode_json = rv.get_json()

    assert rv.mimetype == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"

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


def test_postcode_missing_json(client):
    rv = client.get("/postcodes/14214124")
    assert rv.mimetype == "application/json"
    assert rv.status == "404 NOT FOUND"


def test_postcode_html(client):
    rv = client.get("/postcodes/EX36 4AT.html")
    assert rv.mimetype == "text/html"
    content = rv.data.decode("utf8")
    assert "EX36 4AT" in content
    assert "E01020135" in content


def test_postcode_missing_html(client):
    rv = client.get("/postcodes/14214124.html")
    assert rv.status == "404 NOT FOUND"
    assert rv.mimetype == "text/html"


def test_postcode_redirect(client):
    rv = client.get("/postcodes/redirect?postcode=EX36 4AT")
    assert rv.status_code == 303
    assert rv.mimetype == "text/html"
    assert rv.headers["Location"].endswith("/postcodes/EX36%204AT.html")


def test_postcode_hash(client):
    rv = client.get("/postcodes/hash/abc1.json?properties=ward_code")
    assert rv.mimetype == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert "data" in rv.json
    assert rv.json["data"]


def test_postcode_hash_too_small(client):
    rv = client.get("/postcodes/hash/ab.json?properties=ward_code")
    assert rv.status_code == 400


def test_postcode_hashes(client):
    rv = client.post(
        "/postcodes/hashes.json",
        data=dict(
            hash="abc1",
            properties=["ward_code"],
        ),
    )
    assert rv.mimetype == "application/json"
    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert "data" in rv.json
    assert rv.json["data"]


def test_postcode_hashes_too_small(client):
    rv = client.post(
        "/postcodes/hashes.json",
        data=dict(
            hash="ab",
            properties=["ward_code"],
        ),
    )
    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert rv.status_code == 400

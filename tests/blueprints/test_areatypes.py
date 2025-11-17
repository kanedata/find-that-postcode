import html

AREATYPE_CODE = "lsoa21"


def test_areatype_json(client):
    rv = client.get("/areatypes/{}.json".format(AREATYPE_CODE))
    data = rv.json()

    assert rv.headers["Access-Control-Allow-Origin"] == "*"
    assert (
        data.get("data", {}).get("attributes", {}).get("full_name")
        == "2021 Census Lower Layer Super Output Area (LSOA)/ Data Zone (DZ)/ SOA"
    )
    assert len(data.get("included", [])) == 9


def test_areatype_json_missing(client):
    rv = client.get("/areatypes/{}.json".format("kjhgdskgds"))
    assert rv.status_code == 404


def test_areatype_html(client):
    rv = client.get("/areatypes/{}.html".format(AREATYPE_CODE))
    content = rv.text
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert html.escape("Lower Super Output Area") in content
    assert AREATYPE_CODE in content


def test_areatype_html_missing(client):
    rv = client.get("/areatypes/{}.html".format("kjhgdskgds"))
    assert rv.status_code == 404


def test_areatypes_html(client):
    rv = client.get("/areatypes")
    content = rv.text
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert html.escape("Lower Super Output Area") in content
    assert AREATYPE_CODE in content


def test_areatype_csv(client):
    rv = client.get("/areatypes/{}.csv".format(AREATYPE_CODE))
    content = rv.text
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/csv"
    assert "E01020135" in content

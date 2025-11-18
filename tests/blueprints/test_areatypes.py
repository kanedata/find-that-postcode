import html

import pytest

AREATYPE_CODE = "lsoa21"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/areatypes/{}".format(AREATYPE_CODE),
        "/areatypes/{}.json".format(AREATYPE_CODE),
        "/api/v1/areatypes/{}".format(AREATYPE_CODE),
    ],
)
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_areatype_json(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    data = rv.json()

    assert (
        data.get("data", {}).get("attributes", {}).get("full_name")
        == "2021 Census Lower Layer Super Output Area (LSOA)/ Data Zone (DZ)/ SOA"
    )
    assert len(data.get("included", [])) == 9
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize(
    "endpoint",
    [
        "/areatypes/{}".format("kjhgdskgds"),
        "/areatypes/{}.json".format("kjhgdskgds"),
        "/api/v1/areatypes/{}".format("kjhgdskgds"),
    ],
)
def test_areatype_json_missing(client, endpoint):
    rv = client.get(endpoint)
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
    print(rv.headers)
    print(content)
    assert rv.status_code == 200
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/html"
    assert html.escape("Lower Super Output Area") in content
    assert AREATYPE_CODE in content


def test_areatype_csv(client):
    rv = client.get("/areatypes/{}.csv".format(AREATYPE_CODE))
    content = rv.text
    assert rv.headers["Content-Type"].split(";")[0].strip() == "text/csv"
    assert "E01020135" in content

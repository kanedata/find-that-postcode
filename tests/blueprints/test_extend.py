import json
from urllib.parse import urlencode

import pytest


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_reconcile_spec(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get(endpoint, headers=headers)
    spec = rv.json()
    assert "extend" in spec
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"
    # assert "propose_properties" in spec["extend"]
    # assert "service_url" in spec["extend"]["propose_properties"]
    # assert "service_path" in spec["extend"]["propose_properties"]
    # assert isinstance(spec.get("extend", {}).get("property_settings"), list)
    # assert "name" in spec.get("extend", {}).get("property_settings", [])[0]
    # assert "label" in spec.get("extend", {}).get("property_settings", [])[0]
    # assert spec.get(
    #   "extend", {}
    # ).get(
    #   "property_settings",
    #   []
    # )[0]["type"] in ["number", "text", "checkbox", "select"]


# def test_reconcile_properties(client):
#     rv = client.get('/reconcile/properties?type=testtype')
#     spec = rv.json()

#     assert spec["type"] == "testtype"
#     assert isinstance(spec.get("properties"), list)
#     assert "name" in spec.get("properties", [])[0]
#     assert "id" in spec.get("properties", [])[0]


extend_q = {
    "extend": json.dumps({"ids": ["EX36 4AT"], "properties": [{"id": "lsoa21"}]})
}


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_reconcile_extend(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.get("{}?{}".format(endpoint, urlencode(extend_q)), headers=headers)
    result = rv.json()
    assert rv.status_code == 200
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert "lsoa11" not in result["rows"]["EX36 4AT"]
    assert result["rows"]["EX36 4AT"]["lsoa21"] == "E01020135"
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
def test_reconcile_extend_jsonp(client, endpoint):
    extend_q["callback"] = "testCallback"
    rv = client.get("{}?{}".format(endpoint, urlencode(extend_q)))
    data = rv.text
    assert rv.status_code == 200
    assert data.startswith(extend_q["callback"])

    result = json.loads(data[len(extend_q["callback"]) + 1 : -1])
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert "lsoa11" not in result["rows"]["EX36 4AT"]
    assert result["rows"]["EX36 4AT"]["lsoa21"] == "E01020135"


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_reconcile_extend_post(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.post(endpoint, data=extend_q, headers=headers)
    result = rv.json()
    assert rv.status_code == 200
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert "lsoa11" not in result["rows"]["EX36 4AT"]
    assert result["rows"]["EX36 4AT"]["lsoa21"] == "E01020135"
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
def test_reconcile_extend_post_jsonp(client, endpoint):
    rv = client.post("{}?callback=testCallback".format(endpoint), data=extend_q)
    data = rv.text
    assert rv.status_code == 200
    assert data.startswith("testCallback")

    result = json.loads(data[len("testCallback") + 1 : -1])
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert "lsoa11" not in result["rows"]["EX36 4AT"]
    assert result["rows"]["EX36 4AT"]["lsoa21"] == "E01020135"


recon_q = {
    "queries": json.dumps(
        {
            "q0": {
                "query": "EX36 4AT",
                "type": "/postcode",
            },
            "q1": {
                "query": "North Devon",
                "type": "/area",
            },
        }
    )
}


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_reconcile(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    print("{}?{}".format(endpoint, urlencode(recon_q)))
    rv = client.get("{}?{}".format(endpoint, urlencode(recon_q)), headers=headers)
    result = rv.json()
    assert rv.status_code == 200
    assert "q0" in result
    assert "q1" in result
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"


@pytest.mark.parametrize("endpoint", ["/reconcile", "/api/v1/reconcile/"])
@pytest.mark.parametrize("origin", ["http://example.com", None])
def test_reconcile_post(client, origin, endpoint):
    headers = {}
    check_cors = False
    if origin:
        headers["Origin"] = origin
        check_cors = True
    rv = client.post(endpoint, data=recon_q, headers=headers)
    result = rv.json()
    assert rv.status_code == 200
    assert "q0" in result
    assert "q1" in result
    if check_cors:
        assert rv.headers["Access-Control-Allow-Origin"] == "*"

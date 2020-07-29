from urllib.parse import urlencode
import json

from tests.fixtures import client


def test_reconcile_spec(client):
    rv = client.get('/reconcile')
    spec = rv.get_json()
    assert rv.headers['Access-Control-Allow-Origin'] == '*'
    assert "extend" in spec
    # assert "propose_properties" in spec["extend"]
    # assert "service_url" in spec["extend"]["propose_properties"]
    # assert "service_path" in spec["extend"]["propose_properties"]
    # assert isinstance(spec.get("extend", {}).get("property_settings"), list)
    # assert "name" in spec.get("extend", {}).get("property_settings", [])[0]
    # assert "label" in spec.get("extend", {}).get("property_settings", [])[0]
    # assert spec.get("extend", {}).get("property_settings", [])[0]["type"] in ["number", "text", "checkbox", "select"]

# def test_reconcile_properties(client):
#     rv = client.get('/reconcile/properties?type=testtype')
#     spec = rv.get_json()

#     assert spec["type"] == "testtype"
#     assert isinstance(spec.get("properties"), list)
#     assert "name" in spec.get("properties", [])[0]
#     assert "id" in spec.get("properties", [])[0]


extend_q = {
    "extend": json.dumps({
        "ids": ["EX36 4AT"],
        "properties": [
            {
                "id": "lsoa11"
            }
        ]
    })
}


def test_reconcile_extend(client):
    rv = client.get('/reconcile?{}'.format(urlencode(extend_q)))
    result = rv.get_json()
    assert rv.headers['Access-Control-Allow-Origin'] == '*'
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert result["rows"]["EX36 4AT"]["lsoa11"] == 'E01020135'


def test_reconcile_extend_jsonp(client):
    extend_q["callback"] = "testCallback"
    rv = client.get('/reconcile?{}'.format(urlencode(extend_q)))
    data = rv.data.decode("utf8")
    assert data.startswith(extend_q["callback"])

    result = json.loads(data[len(extend_q["callback"]) + 1:-1])
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert result["rows"]["EX36 4AT"]["lsoa11"] == 'E01020135'


def test_reconcile_extend_post(client):
    rv = client.post('/reconcile', data=extend_q)
    result = rv.get_json()
    assert rv.headers['Access-Control-Allow-Origin'] == '*'
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert result["rows"]["EX36 4AT"]["lsoa11"] == 'E01020135'


def test_reconcile_extend_post_jsonp(client):
    rv = client.post('/reconcile?callback=testCallback', data=extend_q)
    data = rv.data.decode("utf8")
    assert data.startswith("testCallback")

    result = json.loads(data[len("testCallback") + 1:-1])
    assert "meta" in result
    assert "EX36 4AT" in result["rows"]
    assert result["rows"]["EX36 4AT"]["lsoa11"] == 'E01020135'


recon_q = {
    "queries": json.dumps({
        "q0": {
            "query": "EX36 4AT",
            "type": "/postcode",
        },
        "q1": {
            "query": "North Devon",
            "type": "/area",
        },
    })
}


def test_reconcile(client):
    rv = client.get('/reconcile?{}'.format(urlencode(recon_q)))
    result = rv.get_json()
    assert rv.headers['Access-Control-Allow-Origin'] == '*'
    assert "q0" in result
    assert "q1" in result


def test_reconcile_post(client):
    rv = client.post('/reconcile', data=recon_q)
    result = rv.get_json()
    assert rv.headers['Access-Control-Allow-Origin'] == '*'
    assert "q0" in result
    assert "q1" in result

import types

from findthatpostcode.controllers.areas import Area, get_all_areas, search_areas
from findthatpostcode.controllers.postcodes import Postcode
from tests.conftest import MockElasticsearch


def test_area_class():
    a = Area("testentity", {"code": "testentity", "name": "Test Entity"})
    assert a.id == "testentity"
    assert a.attributes["name"] == "Test Entity"
    assert str(a) == "<Area testentity>"


def test_area_class_es():
    es = MockElasticsearch()
    a = Area.get_from_es("S02000783", es)

    assert a.id == "S02000783"
    assert a.attributes["name"] == "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"
    assert str(a) == "<Area S02000783>"

    a = Area.get_from_es("E01020135", es)  # get an area with example postcodes

    assert len(a.relationships["example_postcodes"]) > 0
    assert isinstance(a.relationships["example_postcodes"][0], Postcode)


def test_search_areas():
    es = MockElasticsearch()
    a = search_areas("test", es)

    assert "result" in a
    assert "result_count" in a
    assert a["result_count"] > 0
    assert isinstance(a["result"][0], Area)


def test_get_all_areas():
    es = MockElasticsearch()
    a = get_all_areas(es)

    assert isinstance(a, types.GeneratorType)
    result = [area for area in a]
    assert len(result)

    # @TODO: test this fetches the list of areas - with pagination

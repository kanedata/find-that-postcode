import pytest
from tests.fixtures import MockElasticsearch

from dkpostcodes.controllers.areas import Area, Areas
from dkpostcodes.controllers.postcodes import Postcode

def test_area_class():
    a = Area('testentity', {"code": "testentity", "name": "Test Entity"})
    assert a.id == 'testentity'
    assert a.attributes["name"] == "Test Entity"
    assert str(a) == '<Area testentity>'

def test_area_class_es():

    es = MockElasticsearch()
    a = Area.get_from_es('S02000783', es)
    
    assert a.id == 'S02000783'
    assert a.attributes["name"] == "Lower Bow & Larkfield, Fancy Farm, Mallard Bowl"
    assert str(a) == '<Area S02000783>'

    assert len(a.example_postcodes) > 0
    assert isinstance(a.example_postcodes[0], Postcode)

def test_areas_class():

    a = Areas()
    assert a.id == "__all"
    assert len(a.attributes) == 0

def test_areas_class_es():

    es = MockElasticsearch()
    a = Areas.get_from_es(es)

    assert a.id == "__all"
    assert len(a.attributes) > 0
    assert len(a.areatypes) > 0

    # @TODO: test this fetches the list of areas - with pagination

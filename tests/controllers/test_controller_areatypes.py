import pytest
from tests.fixtures import MockElasticsearch

from dkpostcodes.controllers.areatypes import Areatype, Areatypes
from dkpostcodes.controllers.areas import Area

def test_areatype_class():
    a = Areatype('testentity', {"code": "testentity", "name": "Test Entity"})
    assert a.id == 'testentity'
    assert a.attributes["name"] == "Test Entity"
    assert len(a.areatypes) > 0
    assert str(a) == '<AreaType testentity>'

    # @TODO: test this fetches the list of areas - with pagination

def test_areatypes_class():

    a = Areatypes()
    assert a.id == "__all"
    assert len(a.attributes) == 0
    assert len(a.areatypes) > 0

def test_areatypes_class_es():

    es = MockElasticsearch()
    a = Areatypes.get_from_es(es)

    assert a.id == "__all"
    assert len(a.attributes) > 0
    assert a.attributes[0].doc_count > 0
    assert isinstance(a.attributes[0], Areatype)
    assert len(a.areatypes) > 0

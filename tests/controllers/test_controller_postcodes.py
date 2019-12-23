import pytest
from tests.fixtures import MockElasticsearch

from dkpostcodes.controllers.postcodes import Postcode

def test_postcode_class():
    a = Postcode('testentity', {"code": "testentity", "name": "Test Entity"})
    assert a.id == 'TESTENTITY'
    assert a.attributes["name"] == "Test Entity"
    assert str(a) == '<Postcode TESTENTITY>'

def test_postcode_class_es():

    es = MockElasticsearch()
    a = Postcode.get_from_es('EX36 4AT', es)
    
    assert a.id == 'EX36 4AT'
    assert a.attributes["oseast1m"] == 271505
    assert str(a) == '<Postcode EX36 4AT>'


import pytest
from tests.fixtures import MockElasticsearch

from dkpostcodes.controllers.points import Point

def test_point_class():
    a = Point((100, -100), {"code": "testentity", "name": "Test Entity"})
    assert a.id == (100, -100)
    assert a.attributes["name"] == "Test Entity"
    assert str(a) == '<Point 100, -100>'

def test_point_class_es():

    es = MockElasticsearch()
    a = Point.get_from_es((100, -100), es)
    
    assert a.id == 'EX36 4AT'
    assert a.attributes["closest_postcode"]["oseast1m"] == 271505
    assert str(a) == '<Point 100, -100>'


from findthatpostcode.controllers.areas import Areatype


def test_areatype_class():
    a = Areatype("testentity", {"code": "testentity", "name": "Test Entity"})
    assert a.id == "testentity"
    assert a.attributes["name"] == "Test Entity"
    assert len(a.areatypes) > 0
    assert str(a) == "<AreaType testentity>"

    # @TODO: test this fetches the list of areas - with pagination

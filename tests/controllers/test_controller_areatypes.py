from findthatpostcode.areatypes import AreaTypeEnum
from findthatpostcode.controllers.areas import Areatype


def test_areatype_class():
    a = Areatype(
        AreaTypeEnum.BUA11.value, {"code": "testentity", "name": "Test Entity"}
    )
    assert a.id == AreaTypeEnum.BUA11.value
    assert a.attributes["name"] == "Test Entity"
    assert len(a.areatypes) > 0
    assert str(a) == f"<AreaType {AreaTypeEnum.BUA11.value}>"

    # @TODO: test this fetches the list of areas - with pagination

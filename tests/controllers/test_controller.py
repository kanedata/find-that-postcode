from findthatpostcode.controllers.controller import Controller
from findthatpostcode.settings import POSTCODE_INDEX
from findthatpostcode.utils import ESConfig
from tests.conftest import MockElasticsearch


def test_controller_class():
    id_ = "testentity"
    data = {"code": "testentity", "name": "Test Entity"}

    # test a found entity
    a = Controller(id_, data)
    assert a.id == id_
    assert a.attributes["name"] == data["name"]
    assert a.found is True
    assert len(a.get_errors()) == 0

    # test internal functions
    assert a.parse_id(id_) == id_
    assert a.process_attributes(data) == data

    # test a non existant object
    a = Controller(id_, {})
    assert a.id == id_
    assert a.attributes.get("name") is None
    assert a.found is False
    assert len(a.get_errors()) == 1
    assert a.get_errors()[0]["status"] == "404"


def test_controller_fetch():
    es = MockElasticsearch()

    a = Controller.get_from_es(
        "EX36 4AT",
        es,  # type: ignore
        es_config=ESConfig(es_index=POSTCODE_INDEX, es_type="_doc"),
    )
    assert isinstance(a.id, str)
    assert len(a.attributes) > 4
    assert a.found is True
    assert len(a.get_errors()) == 0

import pytest
from fastapi import HTTPException

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.controller import Controller


def test_return_result_abort():
    controller = Controller("123")
    with pytest.raises(HTTPException):
        return_result(controller, None, filetype="html", template=None)

import pytest
from fastapi import HTTPException

from findthatpostcode.blueprints.utils import return_result


def test_return_result_abort():
    with pytest.raises(HTTPException):
        return_result({}, filetype="html", template=None)

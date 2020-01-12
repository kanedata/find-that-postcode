import pytest
from werkzeug.exceptions import InternalServerError

from findthatpostcode.blueprints.utils import return_result


def test_return_result_abort():
    with pytest.raises(InternalServerError):
        a = return_result({}, filetype='html', template=None)

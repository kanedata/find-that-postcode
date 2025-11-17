from dataclasses import dataclass

from fastapi.responses import PlainTextResponse
from fastapi.templating import Jinja2Templates

from findthatpostcode.settings import TEMPLATES_DIR

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@dataclass
class Field:
    id: str
    name: str
    location: str | None = None
    has_name: bool = False
    area: str | None = None


class CSVResponse(PlainTextResponse):
    media_type = "text/csv"

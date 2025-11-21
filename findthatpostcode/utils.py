import datetime
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask

from findthatpostcode.areatypes import AREA_TYPES
from findthatpostcode.metadata import KEY_AREA_TYPES, OTHER_CODES, STATS_FIELDS
from findthatpostcode.settings import ETHICAL_ADS_PUBLISHER, TEMPLATES_DIR


def clean_postcode(postcode: str | None) -> str:
    """
    standardises a postcode into the correct format
    """
    if not isinstance(postcode, str):
        return ""

    # check for blank/empty
    # put in all caps
    postcode = postcode.strip().upper()
    if postcode == "":
        return ""

    # replace any non alphanumeric characters
    postcode = re.sub("[^0-9a-zA-Z]+", "", postcode)

    # check for nonstandard codes
    if len(postcode) > 7:
        return postcode

    first_part = postcode[:-3].strip()
    last_part = postcode[-3:].strip()

    # check for incorrect characters
    first_part = list(first_part)
    last_part = list(last_part)
    if last_part[0] == "O":
        last_part[0] = "0"

    return "%s %s" % ("".join(first_part), "".join(last_part))


def inject_context(request):
    return dict(
        now=datetime.datetime.now(),
        key_area_types=KEY_AREA_TYPES,
        other_codes=OTHER_CODES,
        area_types=AREA_TYPES,
        ethical_ads_publisher=ETHICAL_ADS_PUBLISHER,
        stats_fields=STATS_FIELDS,
    )


def expand_commas(s):
    if not isinstance(s, str):
        return s
    return re.sub(r"\b,\b", ", ", s)


templates = Jinja2Templates(
    directory=TEMPLATES_DIR, context_processors=[inject_context]
)
templates.env.filters["expand_commas"] = expand_commas


class CSVResponse(PlainTextResponse):
    media_type = "text/csv"


class GeoJSONResponse(JSONResponse):
    media_type = "application/geo+json"


class JSONPResponse(JSONResponse):
    media_type = "application/javascript"

    def __init__(
        self,
        content: Any,
        callback: str = "",
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        self._callback = callback
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        content = super().render(content).decode("utf-8")
        if self._callback:
            content = f"{self._callback}({content})".encode("utf-8")
        return content


@dataclass
class ESConfig:
    es_index: str
    es_type: str = "_doc"
    _source_exclude: list[str] = field(default_factory=list)

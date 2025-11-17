import codecs
import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, Form, Request, UploadFile

from findthatpostcode.blueprints.areas import CSVResponse
from findthatpostcode.blueprints.process_csv import process_csv
from findthatpostcode.controllers.areas import area_types_count
from findthatpostcode.db import ElasticsearchDep
from findthatpostcode.metadata import (
    BASIC_UPLOAD_FIELDS,
    DEFAULT_UPLOAD_FIELDS,
    STATS_FIELDS,
)
from findthatpostcode.utils import templates

bp = APIRouter(prefix="/addtocsv")


@bp.get("/")
def addtocsv(es: ElasticsearchDep, request: Request):
    ats = area_types_count(es)
    return templates.TemplateResponse(
        request=request,
        name="addtocsv.html.j2",
        context={
            "result": ats,
            "basic_fields": BASIC_UPLOAD_FIELDS,
            "stats_fields": STATS_FIELDS,
            "default_fields": DEFAULT_UPLOAD_FIELDS,
        },
        media_type="text/html",
    )


@bp.post("/")
def return_csv(
    es: ElasticsearchDep,
    csvfile: UploadFile,
    column_name: Annotated[str, Form()],
    fields: Annotated[list[str], Form()],
):
    if not fields:
        fields = DEFAULT_UPLOAD_FIELDS

    if "latlng" in fields:
        fields.append("lat")
        fields.append("long")
        fields.remove("latlng")

    if "estnrth" in fields:
        fields.append("oseast1m")
        fields.append("osnrth1m")
        fields.remove("estnrth")

    if "lep" in fields:
        fields.append("lep1")
        fields.append("lep2")
        fields.remove("lep")

    if "lep_name" in fields:
        fields.append("lep1_name")
        fields.append("lep2_name")
        fields.remove("lep_name")

    _, ext = os.path.splitext(csvfile.filename)
    if ext not in [".csv"]:
        return "File extension not allowed."

    with tempfile.SpooledTemporaryFile(mode="w+", newline="") as output:
        process_csv(
            codecs.iterdecode(csvfile.file, "utf-8"),
            output,
            es,
            column_name,
            fields,
        )
        output.seek(0)

        response = CSVResponse(output.read())
        response.headers["Content-Type"] = "text/csv"
        response.headers["Content-Disposition"] = 'attachment; filename="{}"'.format(
            csvfile.filename
        )
        return response

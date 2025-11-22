import csv
import io
import re
from http import HTTPStatus
from typing import Iterator

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

from findthatpostcode.blueprints.utils import return_result
from findthatpostcode.controllers.areas import Area, get_all_areas
from findthatpostcode.db import ElasticsearchDep, S3Dep
from findthatpostcode.utils import CSVResponse, templates

bp = APIRouter(prefix="/areas")

api = APIRouter(prefix="/areas")


@bp.get("/search")
@bp.get("/search.<filetype>")
def area_search(request: Request, filetype="json", q: str | None = None) -> Response:
    redirect_url = request.url_for("search_index")
    if q:
        redirect_url = redirect_url.include_query_params(q=q)
    return RedirectResponse(redirect_url, status_code=HTTPStatus.SEE_OTHER)


@bp.get("/names.csv")
def all_names(es: ElasticsearchDep, types: str = "") -> Response:
    areas = get_all_areas(
        es,
        areatypes=[a.strip().lower() for a in types.split(",") if a],
    )
    return areas_csv(areas, "names.csv")


def areas_csv(areas: Iterator[dict], filename: str) -> Response:
    si = io.StringIO()
    writer = csv.DictWriter(
        si, fieldnames=["code", "name", "type", "active", "date_start", "date_end"]
    )
    writer.writeheader()
    for row in areas:
        if not row.get("name") or not row.get("type"):
            continue
        code = row.get("code")
        if isinstance(code, str) and re.match(r"[A-Z][0-9]{8}", code):
            writer.writerow(row)

    output = CSVResponse(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
    output.headers["Content-type"] = "text/csv"
    return output


@bp.get("/{areacodes}.geojson")
@api.get("/{areacodes}.geojson", name="legacy_get_area_boundary")
def get_area_boundary(areacodes: str, es: ElasticsearchDep, s3_client: S3Dep):
    areacode_list: list[str] = areacodes.split("+")
    features = []
    for areacode in areacode_list:
        result = Area.get_from_es(
            areacode, es, boundary=True, examples_count=0, s3_client=s3_client
        )
        status, r = result.geoJSON()
        if status == HTTPStatus.OK and isinstance(r, dict):
            features.extend(r.get("features", []))
    return {"type": "FeatureCollection", "features": features}


@bp.get("/{areacode}/children/{areatype}.geojson")
@api.get("/{areacode}/children/{areatype}.geojson", include_in_schema=False)
def get_area_children_boundary(
    areacode: str, areatype: str, es: ElasticsearchDep, s3_client: S3Dep
):
    area = Area.get_from_es(areacode, es, boundary=False, examples_count=0)
    features = []
    errors = {}
    if area.relationships["children"]:
        for child_area in area.relationships["children"][areatype]:  # type: ignore
            result = Area.get_from_es(
                child_area.id, es, boundary=True, examples_count=0, s3_client=s3_client
            )
            status, r = result.geoJSON()
            if status == HTTPStatus.OK and isinstance(r, dict):
                features.extend(r.get("features", []))
            else:
                errors[child_area.id] = r
    else:
        errors["area"] = f"No children of type {areatype} found for area {areacode}"
    if not features:
        return JSONResponse(dict(message=errors), status_code=HTTPStatus.NOT_FOUND)
    return {"type": "FeatureCollection", "features": features}


@bp.get("/{areacode}")
@bp.get("/{areacode}.{filetype}")
@api.get("/{areacode}", name="legacy_get_area")
def get_area(
    areacode: str,
    request: Request,
    es: ElasticsearchDep,
    s3_client: S3Dep,
    child: str | None = None,
    filetype: str = "json",
) -> Response:
    result = Area.get_from_es(
        areacode,
        es,
        boundary=(filetype == "geojson"),
        examples_count=(0 if filetype == "geojson" else 5),
        s3_client=s3_client,
    )

    if filetype == "geojson":
        status, r = result.geoJSON()
        if status != HTTPStatus.OK:
            return JSONResponse(content={"message": r}, status_code=status)
        return JSONResponse(r)

    return return_result(
        result,
        request,
        filetype,
        "area.html.j2",
        child=child,
        example_postcode_json=[
            p.attributes.get("location")
            for p in result.relationships["example_postcodes"]  # type: ignore
            if p.attributes.get("location")
        ],
    )


@bp.get("/{areacodes}/map")
def get_area_map(request: Request, areacodes: str) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="area_map.html.j2",
        context={"areacodes": areacodes},
        media_type="text/html",
    )

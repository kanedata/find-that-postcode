"""
Import commands for the register of geographic codes and code history database
"""

import csv
import glob
import io
import json
import os.path
from collections import defaultdict

import click
import requests
import requests_cache
import tqdm
from elasticsearch.helpers import scan
from pyproj import Transformer
from shapely import to_geojson
from shapely.geometry import shape
from shapely.ops import transform

from findthatpostcode.commands.codes import AREA_INDEX
from findthatpostcode.db import get_es, get_s3_client
from findthatpostcode.settings import DEBUG, S3_BUCKET


@click.command("boundaries")
@click.option("--es-index", default=AREA_INDEX)
@click.option("--code-field", default=None)
@click.option("--examine/--no-examine", default=False)
@click.option("--remove/--no-remove", default=False)
@click.argument("urls", nargs=-1)
def import_boundaries(
    urls: list[str],
    examine: bool = False,
    code_field: str | None = None,
    es_index: str = AREA_INDEX,
    remove: bool = False,
):
    if remove:
        # update all instances of area to remove the "boundary" key
        es = get_es()
        es.update_by_query(
            index=es_index,
            body={
                "script": 'ctx._source.remove("boundary")',
                "query": {"exists": {"field": "boundary"}},
            },
        )
        return

    if DEBUG:
        requests_cache.install_cache()

    # initialise the boto3 session
    client = get_s3_client()

    for url in urls:
        if url.startswith("http"):
            import_boundary(client, url, examine, code_field)
        else:
            files = glob.glob(url, recursive=True)
            for file in files:
                import_boundary(client, file, examine, code_field)


def import_boundary(
    client, url: str, examine: bool = False, code_field: str | None = None
):
    boundaries = None
    if url.startswith("http"):
        r = requests.get(url, stream=True)
        boundaries = r.json()
    elif os.path.isfile(url):
        with open(url, encoding="latin1") as f:
            boundaries = json.load(f)
    else:
        raise ValueError(f"Invalid URL or file path: {url}")

    errors = []

    # Check the CRS
    transformer = None
    if boundaries.get("crs", {}).get("properties", {}).get("name") == "EPSG:27700":
        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    # find the code field for a boundary
    if len(boundaries.get("features", [])) == 0:
        errors.append("[ERROR][{}] Features not found in file".format(url))
    if len(boundaries.get("features", [])) > 0 and not code_field:
        test_boundary = boundaries.get("features", [])[0]
        code_fields = []
        for k in test_boundary.get("properties", {}):
            if k.lower().endswith("cd"):
                code_fields.append(k)
        if len(code_fields) == 1:
            code_field = code_fields[0]
        elif len(code_fields) == 0:
            errors.append("[ERROR][{}] No code field found in file".format(url))
        else:
            errors.append("[ERROR][{}] Too many code fields found in file".format(url))
            errors.append(
                "[ERROR][{}] Code fields: {}".format(url, "; ".join(code_fields))
            )

    if len(errors) > 0:
        if examine:
            for e in errors:
                click.echo(e, err=True)
        else:
            raise ValueError("; ".join(errors))

    if code_field is None:
        raise ValueError("No code field specified")
    code = code_field.lower().replace("cd", "")

    if examine:
        click.echo("[{}] Opened file: [{}]".format(code, url))
        click.echo("[{}] Looking for code field: [{}]".format(code, code_field))
        click.echo("[{}] Geojson type: [{}]".format(code, boundaries["type"]))
        click.echo(
            "[{}] Number of features [{}]".format(code, len(boundaries["features"]))
        )
        for k, i in enumerate(boundaries["features"][:5]):
            click.echo("[{}] Feature {} type {}".format(code, k, i["type"]))
            click.echo(
                "[{}] Feature {} properties {}".format(
                    code, k, list(i["properties"].keys())
                )
            )
            click.echo(
                "[{}] Feature {} geometry type {}".format(
                    code, k, i["geometry"]["type"]
                )
            )
            click.echo(
                "[{}] Feature {} geometry length {}".format(
                    code, k, len(str(i["geometry"]["coordinates"]))
                )
            )
            if code_field in i["properties"]:
                click.echo(
                    "[{}] Feature {} Code {}".format(
                        code, k, i["properties"][code_field]
                    )
                )
            else:
                click.echo(
                    "[ERROR][{}] Feature {} Code field not found".format(code, k),
                    err=True,
                )
    else:
        click.echo("[{}] Opened file: [{}]".format(code, url))
        click.echo(
            "[{}] {} features to import".format(code, len(boundaries["features"]))
        )
        boundary_count = 0
        errors = []
        for k, i in tqdm.tqdm(
            enumerate(boundaries["features"]), total=len(boundaries["features"])
        ):
            area_code = i["properties"][code_field]
            prefix = area_code[0:3]
            if transformer:
                # create a shapely object from the geometry
                geometry = shape(i["geometry"])
                i["geometry"] = json.loads(
                    to_geojson(
                        transform(
                            transformer.transform,
                            geometry,
                        )
                    )
                )

            client.upload_fileobj(
                io.BytesIO(json.dumps(i).encode("utf-8")),
                S3_BUCKET,
                "{}/{}.json".format(prefix, area_code),
            )
            boundary_count += 1
        click.echo("[{}] {} boundaries imported".format(code, boundary_count))


@click.command("boundaries")
@click.option("--es-index", default=AREA_INDEX)
def check_boundaries(es_index=AREA_INDEX):
    # Get list of all areas from ES
    es = get_es()

    areas = defaultdict(dict)
    area_search = scan(
        es,
        query={
            "query": {"match_all": {}},
        },
        index=es_index,
        _source_includes=["active"],
    )

    for area in tqdm.tqdm(area_search):
        prefix = area["_id"][0:3]
        areas[prefix][area["_id"]] = {
            "boundary": False,
            "active": area["_source"]["active"],
        }

    # Get list of all boundaries from S3
    s3_client = get_s3_client()
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=S3_BUCKET)
    for page in tqdm.tqdm(page_iterator):
        for obj in page.get("Contents", []):
            if obj.get("Key", "").endswith(".json"):
                bucket, prefix, code = (
                    obj.get("Key", "").replace(".json", "").split("/")
                )
                if prefix in areas and code in areas[prefix]:
                    areas[prefix][code]["boundary"] = True

    # Check that all areas have a boundary
    with open("boundaries.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "prefix",
                "total_areas",
                "total_with_boundary",
                "total_active",
                "total_active_with_boundary",
            ],
        )
        writer.writeheader()
        for prefix, area_list in areas.items():
            row = {
                "prefix": prefix,
                "total_areas": 0,
                "total_with_boundary": 0,
                "total_active": 0,
                "total_active_with_boundary": 0,
            }
            for i in area_list.values():
                row["total_areas"] += 1
                if i["boundary"]:
                    row["total_with_boundary"] += 1
                if i["active"]:
                    row["total_active"] += 1
                if i["boundary"] and i["active"]:
                    row["total_active_with_boundary"] += 1
            writer.writerow(row)

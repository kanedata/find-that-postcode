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
from boto3 import session
from elasticsearch.helpers import scan
from pyproj import Transformer
from shapely import to_geojson
from shapely.geometry import shape
from shapely.ops import transform

from findthatpostcode.commands.codes import AREA_INDEX
from findthatpostcode.db import get_es, get_s3_client
from findthatpostcode.settings import (
    DEBUG,
    S3_ACCESS_ID,
    S3_BUCKET,
    S3_ENDPOINT,
    S3_REGION,
    S3_SECRET_KEY,
)


@click.command("boundaries")
@click.option("--es-index", default=AREA_INDEX)
@click.option("--code-field", default=None)
@click.option("--examine/--no-examine", default=False)
@click.option("--remove/--no-remove", default=False)
@click.argument("urls", nargs=-1)
def import_boundaries(
    urls, examine=False, code_field=None, es_index=AREA_INDEX, remove=False
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


def import_boundary(client, url, examine=False, code_field=None):
    if url.startswith("http"):
        r = requests.get(url, stream=True)
        boundaries = r.json()
    elif os.path.isfile(url):
        with open(url, encoding="latin1") as f:
            boundaries = json.load(f)
    errors = []

    # Check the CRS
    transformer = None
    if boundaries.get("crs", {}).get("properties", {}).get("name") == "EPSG:27700":
        transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    # find the code field for a boundary
    if len(boundaries.get("features", [])) == 0:
        errors.append("[ERROR][%s] Features not found in file" % (url,))
    if len(boundaries.get("features", [])) > 0 and not code_field:
        test_boundary = boundaries.get("features", [])[0]
        code_fields = []
        for k in test_boundary.get("properties", {}):
            if k.lower().endswith("cd"):
                code_fields.append(k)
        if len(code_fields) == 1:
            code_field = code_fields[0]
        elif len(code_fields) == 0:
            errors.append("[ERROR][%s] No code field found in file" % (url,))
        else:
            errors.append("[ERROR][%s] Too many code fields found in file" % (url,))
            errors.append("[ERROR][%s] Code fields: %s" % (url, "; ".join(code_fields)))

    if len(errors) > 0:
        if examine:
            for e in errors:
                print(e)
        else:
            raise ValueError("; ".join(errors))

    code = code_field.lower().replace("cd", "")

    if examine:
        print("[%s] Opened file: [%s]" % (code, url))
        print("[%s] Looking for code field: [%s]" % (code, code_field))
        print("[%s] Geojson type: [%s]" % (code, boundaries["type"]))
        print("[%s] Number of features [%s]" % (code, len(boundaries["features"])))
        for k, i in enumerate(boundaries["features"][:5]):
            print("[%s] Feature %s type %s" % (code, k, i["type"]))
            print(
                "[%s] Feature %s properties %s"
                % (code, k, list(i["properties"].keys()))
            )
            print("[%s] Feature %s geometry type %s" % (code, k, i["geometry"]["type"]))
            print(
                "[%s] Feature %s geometry length %s"
                % (code, k, len(str(i["geometry"]["coordinates"])))
            )
            if code_field in i["properties"]:
                print(
                    "[%s] Feature %s Code %s" % (code, k, i["properties"][code_field])
                )
            else:
                print(
                    "[ERROR][%s] Feature %s Code field not found"
                    % (
                        code,
                        k,
                    )
                )

    else:
        print("[%s] Opened file: [%s]" % (code, url))
        print("[%s] %s features to import" % (code, len(boundaries["features"])))
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
                "%s/%s.json" % (prefix, area_code),
            )
            boundary_count += 1
        print("[%s] %s boundaries imported" % (code, boundary_count))


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
    s3_session = session.Session()
    s3_client = s3_session.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT.replace(S3_BUCKET + ".", ""),
        aws_access_key_id=S3_ACCESS_ID,
        aws_secret_access_key=S3_SECRET_KEY,
    )
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=S3_BUCKET)
    for page in tqdm.tqdm(page_iterator):
        for obj in page["Contents"]:
            if obj["Key"].endswith(".json"):
                bucket, prefix, code = obj["Key"].replace(".json", "").split("/")
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

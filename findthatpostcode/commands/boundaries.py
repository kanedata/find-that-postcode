"""
Import commands for the register of geographic codes and code history database
"""
import glob
import json
import os.path

import click
import requests
import requests_cache
import shapely.geometry
import tqdm
from elasticsearch.helpers import bulk
from flask import current_app
from flask.cli import with_appcontext

from .. import db
from .codes import AREA_INDEX


@click.command("boundaries")
@click.option("--es-index", default=AREA_INDEX)
@click.option("--code-field", default=None)
@click.option("--examine/--no-examine", default=False)
@click.argument("urls", nargs=-1)
@with_appcontext
def import_boundaries(urls, examine=False, code_field=None, es_index=AREA_INDEX):

    if current_app.config["DEBUG"]:
        requests_cache.install_cache()

    es = db.get_db()

    for url in urls:
        if url.startswith("http"):
            import_boundary(es, url, examine, es_index, code_field)
        else:
            files = glob.glob(url, recursive=True)
            for file in files:
                import_boundary(es, file, examine, es_index, code_field)


def import_boundary(es, url, examine=False, es_index=AREA_INDEX, code_field=None):
    if url.startswith("http"):
        r = requests.get(url, stream=True)
        boundaries = r.json()
    elif os.path.isfile(url):
        with open(url) as f:
            boundaries = json.load(f)
    errors = []

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
        bulk_boundaries = []
        errors = []
        for k, i in tqdm.tqdm(
            enumerate(boundaries["features"]), total=len(boundaries["features"])
        ):
            shp = shapely.geometry.shape(i["geometry"]).buffer(0)
            boundary = {
                "_index": es_index,
                "_type": "_doc",
                "_op_type": "update",
                "_id": i["properties"][code_field],
                "doc": {
                    "boundary": shp.wkt,
                    "has_boundary": True,
                },
            }
            bulk_boundaries.append(boundary)

        # @TODO Log errors somewhere...
        print("[boundaries] Processed %s boundaries" % len(bulk_boundaries))
        print("[elasticsearch] %s boundaries to save" % len(bulk_boundaries))
        results = bulk(es, bulk_boundaries, raise_on_error=False)
        print(
            "[elasticsearch] saved %s boundaries to %s index" % (results[0], es_index)
        )
        print("[elasticsearch] %s errors reported:" % len(results[1]))
        for i in results[1]:
            print(
                " - {} {}".format(
                    i.get("update", {}).get("_id", ""),
                    i.get("update", {})
                    .get("error", {})
                    .get("caused_by", {})
                    .get("type", ""),
                )
            )

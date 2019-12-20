"""
Import commands for the register of geographic codes and code history database
"""
import zipfile
import io
import codecs
import csv
import datetime
from collections import defaultdict

import click
from flask import Flask
from flask.cli import with_appcontext
import requests
import requests_cache
from elasticsearch.helpers import bulk
import tqdm

from .. import db
from .codes import AREA_INDEX

requests_cache.install_cache()

@click.command('boundaries')
@click.option('--es-index', default=AREA_INDEX)
@click.option('--examine/--no-examine', default=False)
@click.argument('urls', nargs=-1)
@with_appcontext
def import_boundaries(urls, examine=False, es_index=AREA_INDEX):

    es = db.get_db()

    for url in urls:
        import_boundary(es, url, examine, es_index)

def import_boundary(es, url, examine=False, es_index=AREA_INDEX):
    r = requests.get(url, stream=True)
    boundaries = r.json()
    errors = []

    # find the code field for a boundary
    if len(boundaries.get("features", [])) > 0:
        test_boundary = boundaries.get("features", [])[0]
        code_fields = []
        for k in test_boundary.get("properties", {}):
            if k.endswith("cd"):
                code_fields.append(k)
        if len(code_fields) == 1:
            code_field = code_fields[0]
        elif len(code_fields) == 0:
            errors.append("[ERROR][%s] No code field found in file" % (boundary_file,))
        else:
            errors.append("[ERROR][%s] Too many code fields found in file" % (boundary_file,))
            errors.append("[ERROR][%s] Code fields: %s" % (boundary_file,"; ".join(code_fields)))
    else:
        errors.append("[ERROR][%s] Features not found in file" % (boundary_file,))

    if len(errors) > 0:
        if args.examine:
            for e in errors:
                print(e)
        else:
            raise ValueError("; ".join(errors))

    code = code_field.replace("cd", "")
    
    if examine:
        print("[%s] Opened file: [%s]" % (code, url))
        print("[%s] Looking for code field: [%s]" % (code, code_field))
        print("[%s] Geojson type: [%s]" % (code, boundaries["type"]))
        print("[%s] Number of features [%s]" % (code, len(boundaries["features"])))
        for k, i in enumerate(boundaries["features"][:5]):
            print("[%s] Feature %s type %s" % (code, k, i["type"]))
            print("[%s] Feature %s properties %s" % (code, k, list(i["properties"].keys())))
            print("[%s] Feature %s geometry type %s" % (code, k, i["geometry"]["type"]))
            print("[%s] Feature %s geometry length %s" % (code, k, len(str(i["geometry"]["coordinates"]))))
            if code_field in i["properties"]:
                print("[%s] Feature %s Code %s" % (code, k, i["properties"][code_field]))
            else:
                print("[ERROR][%s] Feature %s Code field not found" % (code, k,))

    else:
        print("[%s] Opened file: [%s]" % (code, url))
        print("[%s] %s features to import" % (code, len(boundaries["features"])))
        bulk_boundaries = []
        errors = []
        boundaries_updated = 0
        for k, i in enumerate(boundaries["features"]):
            boundary = {
                "_index": es_index,
                "_type": "_doc",
                "_op_type": "update",
                "_id": i["properties"][code_field],
                "doc": {
                    "boundary": {
                        "type": i["geometry"]["type"].lower(),
                        "coordinates": i["geometry"]["coordinates"]
                    },
                    "has_boundary": True
                }
            }
            bulk_boundaries.append(boundary)

        # @TODO Log errors somewhere...
        print("[boundaries] Processed %s boundaries" % len(bulk_boundaries))
        print("[elasticsearch] %s boundaries to save" % len(bulk_boundaries))
        results = bulk(es, bulk_boundaries)
        print("[elasticsearch] saved %s boundaries to %s index" % (results[0], es_index))
        print("[elasticsearch] %s errors reported" % len(results[1]))

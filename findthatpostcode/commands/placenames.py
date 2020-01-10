"""
Import commands for placenames
"""
import zipfile
import io
import codecs
import csv
import datetime
from collections import defaultdict

import click
from flask import Flask, current_app
from flask.cli import with_appcontext
import requests
import requests_cache
from elasticsearch.helpers import bulk
import tqdm

from .. import db

PLACENAMES_INDEX = 'geo_placename'

PLACENAMES_URL = 'https://www.arcgis.com/sharing/rest/content/items/e8e725daf8944af6a336a9d183114697/data'

AREA_LOOKUP = [
    ("cty15cd", "cty", "cty15nm"),
    ("lad15cd", "laua", "lad15nm"),
    ("wd15cd", "ward", None),
    ("par15cd", "parish", None),
    ("hlth12cd", "hlth", 'hlth12nm'),
    ("regd15cd", "rgd", "regd15nm"),
    ("rgn15cd", "rgn", "rgn15nm"),
    ("npark15cd", "park", "npark15nm"),
    ("bua11cd", "bua11", None),
    ("pcon15cd", "pcon", "pcon15nm"),
    ("eer15cd", "eer", "eer15nm"),
    ("pfa15cd", "pfa", "pfa15nm"),
    ("cty18cd", "cty", "cty18nm"),
    ("lad18cd", "laua", "lad18nm"),
    ("wd18cd", "ward", None),
    ("par18cd", "parish", None),
    ("hlth12cd", "hlth", 'hlth12nm'),
    ("regd18cd", "rgd", "regd18nm"),
    ("rgn18cd", "rgn", "rgn18nm"),
    ("npark17cd", "park", "npark17nm"),
    ("bua11cd", "bua11", None),
    ("pcon18cd", "pcon", "pcon18nm"),
    ("eer18cd", "eer", "eer18nm"),
    ("pfa18cd", "pfa", "pfa18nm"),
]

@click.command('placenames')
@click.option('--es-index', default=PLACENAMES_INDEX)
@click.option('--url', default=PLACENAMES_URL)
@with_appcontext
def import_placenames(url=PLACENAMES_URL, es_index=PLACENAMES_INDEX):

    if current_app.config["DEBUG"]:
        requests_cache.install_cache()

    es = db.get_db()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    placenames = []

    for f in z.filelist:
        if not f.filename.endswith(".csv"):
            continue

        print("[placenames] Opening %s" % f.filename)

        with z.open(f, 'r') as pccsv:
            pccsv = io.TextIOWrapper(pccsv)
            reader = csv.DictReader(pccsv)
            for i in reader:
                record = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": i["place18cd"],
                    "doc_as_upsert": True,
                }

                for k in i:
                    if i[k] == "":
                        i[k] = None

                # population count
                if i.get("popcnt"):
                    i["popcnt"] = int(i["popcnt"])

                # latitude and longitude
                for j in ["lat", "long"]:
                    if i[j]:
                        i[j] = float(i[j])
                        if i[j] == 99.999999 or i[j] == 0:
                            i[j] = None
                if i["lat"] and i["long"]:
                    i["location"] = {"lat": i["lat"], "lon": i["long"]}

                # get areas
                areas = {}
                for j in AREA_LOOKUP:
                    if j[0] in i:
                        areas[j[1]] = i[j[0]]
                        del i[j[0]]
                        if j[2] and j[2] in i:
                            del i[j[2]]
                i["areas"] = areas

                record["doc"] = i
                placenames.append(record)

            print("[placenames] Processed %s placenames" % len(placenames))
            print("[elasticsearch] %s placenames to save" % len(placenames))
            results = bulk(es, placenames)
            print("[elasticsearch] saved %s placenames to %s index" % (results[0], es_index))
            print("[elasticsearch] %s errors reported" % len(results[1]))
            placenames = []

"""
Import commands for placenames
"""
import csv
import io
import zipfile

import click
import requests
import requests_cache
from elasticsearch.helpers import bulk
from flask import current_app
from flask.cli import with_appcontext

from .. import db

PLACENAMES_INDEX = "geo_placename"

PLACENAMES_URL = "https://www.arcgis.com/sharing/rest/content/items/6cb9092a37da4b5ea1b5f8b054c343aa/data"

PLACE_TYPES = {
    "BUA": ["Built-up Area", "England and Wales"],
    "BUASD": ["Built-up Area Sub-Division", "England and Wales"],
    "CA": ["Council Area", "Scotland"],
    "CED": ["County Electoral Division", "England"],
    "COM": ["Community", "Wales"],
    "CTY": ["County", "England"],
    "CTYHIST": ["Historic County", "Great Britain"],
    "CTYLT": ["Lieutenancy County", "Great Britain"],
    "LOC": ["Locality", "Great Britain"],
    "LONB": ["London Borough", "England"],
    "MD": ["Metropolitan District", "England"],
    "NMD": ["Non-metropolitan District", "England"],
    "NPARK": ["National Park Great", "Britain"],
    "PAR": ["Civil Parish", "England and Scotland"],
    "RGN": ["Region", "England"],
    "UA": ["Unitary Authority", "England and Wales"],
    "WD": ["Electoral Ward/Division", "Great Britain"],
}

AREA_LOOKUP = [
    ("cty15cd", "cty", "cty15nm"),
    ("lad15cd", "laua", "lad15nm"),
    ("wd15cd", "ward", None),
    ("par15cd", "parish", None),
    ("hlth12cd", "hlth", "hlth12nm"),
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
    ("hlth12cd", "hlth", "hlth12nm"),
    ("regd18cd", "rgd", "regd18nm"),
    ("rgn18cd", "rgn", "rgn18nm"),
    ("npark17cd", "park", "npark17nm"),
    ("bua11cd", "bua11", None),
    ("pcon18cd", "pcon", "pcon18nm"),
    ("eer18cd", "eer", "eer18nm"),
    ("pfa18cd", "pfa", "pfa18nm"),
]


@click.command("placenames")
@click.option("--es-index", default=PLACENAMES_INDEX)
@click.option("--url", default=PLACENAMES_URL)
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

        with z.open(f, "r") as pccsv:
            pccsv = io.TextIOWrapper(pccsv, encoding="latin1")
            reader = csv.DictReader(pccsv)
            place_code = None
            place_name = None
            for i in reader:
                # get the names of the name and code fields
                if not place_code or not place_name:
                    for key in i.keys():
                        if key.startswith("place") and key.endswith("cd"):
                            place_code = key
                        if key.startswith("place") and key.endswith("nm"):
                            place_name = key

                record = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": i[place_code],
                    "doc_as_upsert": True,
                }

                for k in i:
                    if i[k] == "":
                        i[k] = None

                # set the name
                i["name"] = i[place_name]
                del i[place_name]

                # set splitind
                if "splitind" in i:
                    i["splitind"] = i["splitind"] == "1"

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
                i["type"], i["country"] = PLACE_TYPES.get(
                    i["descnm"], [i["descnm"], "United Kingdom"]
                )

                record["doc"] = i
                placenames.append(record)

            print("[placenames] Processed %s placenames" % len(placenames))
            print("[elasticsearch] %s placenames to save" % len(placenames))
            results = bulk(es, placenames)
            print(
                "[elasticsearch] saved %s placenames to %s index"
                % (results[0], es_index)
            )
            print("[elasticsearch] %s errors reported" % len(results[1]))
            placenames = []

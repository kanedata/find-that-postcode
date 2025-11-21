"""
Import commands for placenames
"""

import csv
import io
import zipfile

import click
import requests
import requests_cache

from findthatpostcode.commands.utils import bulk_upload, get_latest_geoportal_url
from findthatpostcode.db import get_es
from findthatpostcode.settings import DEBUG, PLACENAME_INDEX

PRD_IPN = "PRD_IPN"

PLACE_TYPES: dict[str, tuple[str, str]] = {
    "BUA": ("Built-up Area", "England and Wales"),
    "BUASD": ("Built-up Area Sub-Division", "England and Wales"),
    "CA": ("Council Area", "Scotland"),
    "CED": ("County Electoral Division", "England"),
    "COM": ("Community", "Wales"),
    "CTY": ("County", "England"),
    "CTYHIST": ("Historic County", "Great Britain"),
    "CTYLT": ("Lieutenancy County", "Great Britain"),
    "LOC": ("Locality", "Great Britain"),
    "LONB": ("London Borough", "England"),
    "MD": ("Metropolitan District", "England"),
    "NMD": ("Non-metropolitan District", "England"),
    "NPARK": ("National Park Great", "Britain"),
    "PAR": ("Civil Parish", "England and Scotland"),
    "RGN": ("Region", "England"),
    "UA": ("Unitary Authority", "England and Wales"),
    "WD": ("Electoral Ward/Division", "Great Britain"),
}

AREA_LOOKUP: list[tuple[str, str, str | None]] = [
    ("bua11cd", "bua11", None),
    ("bua22cd", "bua22", None),
    ("cty15cd", "cty", "cty15nm"),
    ("lad15cd", "laua", "lad15nm"),
    ("wd15cd", "ward", None),
    ("par15cd", "parish", None),
    ("hlth12cd", "hlth", "hlth12nm"),
    ("regd15cd", "rgd", "regd15nm"),
    ("rgn15cd", "rgn", "rgn15nm"),
    ("npark15cd", "park", "npark15nm"),
    ("pcon15cd", "pcon", "pcon15nm"),
    ("eer15cd", "eer", "eer15nm"),
    ("pfa15cd", "pfa", "pfa15nm"),
    ("cty18cd", "cty", "cty18nm"),
    ("lad18cd", "laua", "lad18nm"),
    ("wd18cd", "ward", None),
    ("par18cd", "parish", None),
    ("regd18cd", "rgd", "regd18nm"),
    ("rgn18cd", "rgn", "rgn18nm"),
    ("npark17cd", "park", "npark17nm"),
    ("pcon18cd", "pcon", "pcon18nm"),
    ("eer18cd", "eer", "eer18nm"),
    ("pfa18cd", "pfa", "pfa18nm"),
    ("cty23cd", "cty", "cty23nm"),
    ("lad23cd", "laua", "lad23nm"),
    ("wd23cd", "ward", None),
    ("par23cd", "parish", None),
    ("hlth23cd", "hlth", "hlth23nm"),
    ("regd23cd", "rgd", "regd23nm"),
    ("rgn23cd", "rgn", "rgn23nm"),
    ("npark23cd", "park", "npark23nm"),
    ("pcon23cd", "pcon", "pcon23nm"),
    ("eer23cd", "eer", "eer23nm"),
    ("pfa23cd", "pfa", "pfa23nm"),
]


@click.command("placenames")
@click.option("--es-index", default=PLACENAME_INDEX)
@click.option("--url", default=None)
def import_placenames(url=None, es_index=PLACENAME_INDEX):
    if DEBUG:
        requests_cache.install_cache()

    if not url:
        url = get_latest_geoportal_url(PRD_IPN)

    es = get_es()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    placenames = []

    for f in z.filelist:
        if not f.filename.endswith(".csv"):
            continue

        click.echo("[placenames] Opening {}".format(f.filename))

        with z.open(f, "r") as pccsv:
            pccsv = io.TextIOWrapper(pccsv, encoding="latin1")
            reader = csv.DictReader(pccsv)
            place_code = None
            place_name = None
            for row in reader:
                # get the names of the name and code fields
                if not place_code or not place_name:
                    for key in row.keys():
                        if key.startswith("place") and key.endswith("cd"):
                            place_code = key
                        if key.startswith("place") and key.endswith("nm"):
                            place_name = key

                record = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": row[place_code],
                    "doc_as_upsert": True,
                }

                for k in row:
                    if row[k] == "":
                        row[k] = None

                # set the name
                row["name"] = row[place_name]
                del row[place_name]

                # set splitind
                if "splitind" in row:
                    row["splitind"] = row["splitind"] == "1"

                # population count
                if row.get("popcnt"):
                    row["popcnt"] = int(row["popcnt"])

                # latitude and longitude
                for j in ["lat", "long"]:
                    if row[j]:
                        row[j] = float(row[j])
                        if row[j] == 99.999999 or row[j] == 0:
                            row[j] = None
                if row["lat"] and row["long"]:
                    row["location"] = {"lat": row["lat"], "lon": row["long"]}

                # get areas
                areas = {}
                for code_field, area_type, name_field in AREA_LOOKUP:
                    if code_field in row:
                        areas[area_type] = row[code_field]
                        del row[code_field]
                        if name_field and name_field in row:
                            del row[name_field]
                row["areas"] = areas
                row["type"], row["country"] = PLACE_TYPES.get(
                    row["descnm"], (row["descnm"], "United Kingdom")
                )

                record["doc"] = row
                placenames.append(record)

            bulk_upload(placenames, es, es_index, "placenames")
            placenames = []

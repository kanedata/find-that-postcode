"""
Import commands for the register of geographic codes and code history database
"""

import csv
import datetime
import hashlib
import io
import zipfile

import click
import requests
import requests_cache
from elasticsearch.helpers import bulk
from flask import current_app
from flask.cli import with_appcontext

from findthatpostcode import db
from findthatpostcode.commands.utils import get_latest_geoportal_url

PC_INDEX = "geo_postcode"
PRD_NSPL = "PRD_NSPL"


@click.command("nspl")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=None)
@with_appcontext
def import_nspl(url=None, es_index=PC_INDEX):
    if not url:
        url = get_latest_geoportal_url(PRD_NSPL)

    if current_app.config["DEBUG"]:
        requests_cache.install_cache()

    es = db.get_db()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    postcodes = []

    for f in z.filelist:
        if not f.filename.endswith(".csv") or not f.filename.startswith(
            "Data/multi_csv/NSPL"
        ):
            continue

        print("[postcodes] Opening %s" % f.filename)

        pcount = 0
        with z.open(f, "r") as pccsv:
            pccsv = io.TextIOWrapper(pccsv)
            reader = csv.DictReader(pccsv)
            for i in reader:
                record = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": i["pcds"],
                    "doc_as_upsert": True,
                }

                # null any blank fields (or ones with a dummy code in)
                for k in i:
                    if i[k] == "" or i[k] in [
                        "E99999999",
                        "S99999999",
                        "W99999999",
                        "N99999999",
                    ]:
                        i[k] = None

                # date fields
                for j in ["dointr", "doterm"]:
                    if i[j]:
                        i[j] = datetime.datetime.strptime(i[j], "%Y%m")

                # latitude and longitude
                for j in ["lat", "long"]:
                    if i[j]:
                        i[j] = float(i[j])
                        if i[j] == 99.999999:
                            i[j] = None
                if i["lat"] and i["long"]:
                    i["location"] = {"lat": i["lat"], "lon": i["long"]}

                rename_fields = {
                    "east1m": "oseast1m",
                    "north1m": "osnrth1m",
                    "usrtypind": "usertype",
                    "gridind": "osgrdind",
                    "oa21cd": "oa21",
                    "cty25cd": "cty",
                    "ced25cd": "ced",
                    "lad25cd": "lad",
                    "wd25cd": "wd",
                    "nhser24cd": "nhser",
                    "ctry25cd": "ctry",
                    "rgn25cd": "rgn",
                    "pcon24cd": "pcon",
                    "ttwa15cd": "ttwa",
                    "itl25cd": "itl",
                    "npark16cd": "park",
                    "lsoa21cd": "lsoa21",
                    "msoa21cd": "msoa21",
                    "wz11cd": "wz11",
                    "sicbl24cd": "sicbl",
                    "bua24cd": "bua24",
                    "ruc21ind": "ruc21",
                    "oac11ind": "oac11",
                    "lep21cd1": "lep1",
                    "lep21cd2": "lep2",
                    "pfa23cd": "pfa",
                    "imd20ind": "imd",
                    "icb23cd": "icb",
                }
                for old, new in rename_fields.items():
                    if old in i:
                        i[new] = i.pop(old)

                # integer fields
                for j in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
                    if i[j]:
                        i[j] = int(i[j])

                # add postcode hash
                i["hash"] = hashlib.md5(
                    i["pcds"].lower().replace(" ", "").encode()
                ).hexdigest()

                record["doc"] = i
                postcodes.append(record)
                pcount += 1

            print("[postcodes] Processed %s postcodes" % pcount)
            print("[elasticsearch] %s postcodes to save" % len(postcodes))
            results = bulk(es, postcodes)
            print(
                "[elasticsearch] saved %s postcodes to %s index"
                % (results[0], es_index)
            )
            print("[elasticsearch] %s errors reported" % len(results[1]))
            postcodes = []

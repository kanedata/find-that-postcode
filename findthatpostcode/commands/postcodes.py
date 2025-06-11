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

from .. import db

PC_INDEX = "geo_postcode"

NSPL_URL = {
    2011: "https://www.arcgis.com/sharing/rest/content/items/521edce4159a451a932539b7fc786322/data",
    2021: "https://www.arcgis.com/sharing/rest/content/items/077631e063eb4e1ab43575d01381ec33/data",
}
DEFAULT_YEAR = 2021


@click.command("nspl")
@click.option("--es-index", default=PC_INDEX)
@click.option("--url", default=None)
@click.option("--year", default=DEFAULT_YEAR, type=int)
@with_appcontext
def import_nspl(url=None, es_index=PC_INDEX, year=DEFAULT_YEAR):
    if not url:
        url = NSPL_URL[year]

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

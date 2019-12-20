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

requests_cache.install_cache()

PC_INDEX = 'geo_postcode'

NSPL_URL = 'https://www.arcgis.com/sharing/rest/content/items/ad7fd1d95f06431aaaceecdce4985c7e/data'
ONSPD_URL = 'https://www.arcgis.com/sharing/rest/content/items/ae45e39fdafe4520bba99c760c303109/data'

@click.command('nspl')
@click.option('--es-index', default=PC_INDEX)
@click.option('--url', default=NSPL_URL)
@with_appcontext
def import_nspl(url=NSPL_URL, es_index=PC_INDEX):

    es = db.get_db()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    postcodes = []

    for f in z.filelist:
        if not f.filename.endswith(".csv") or not f.filename.startswith("Data/multi_csv/NSPL_"):
            continue

        print("[postcodes] Opening %s" % f.filename)

        pcount = 0
        with z.open(f, 'r') as pccsv:
            pccsv = io.TextIOWrapper(pccsv)
            reader = csv.DictReader(pccsv)
            for i in reader:
                # Skip Northern Irish postcodes as not allowed by license
                # https://www.ons.gov.uk/methodology/geography/licences
                if i["pcds"].lower().startswith('bt'):
                    continue
                
                record = {
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": i["pcds"],
                    "doc_as_upsert": True,
                }

                # null any blank fields
                for k in i:
                    if i[k] == "":
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

                record["doc"] = i
                postcodes.append(record)
                pcount += 1

            print("[postcodes] Processed %s postcodes" % pcount)
            print("[elasticsearch] %s postcodes to save" % len(postcodes))
            results = bulk(es, postcodes)
            print("[elasticsearch] saved %s postcodes to %s index" % (results[0], es_index))
            print("[elasticsearch] %s errors reported" % len(results[1]))
            postcodes = []

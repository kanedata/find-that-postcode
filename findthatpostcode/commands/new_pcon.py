import codecs
import csv
import io
import zipfile
from collections import defaultdict

import click
import requests
import requests_cache
import tqdm

from findthatpostcode.commands.codes import AREA_INDEX
from findthatpostcode.commands.postcodes import PC_INDEX
from findthatpostcode.commands.utils import bulk_upload
from findthatpostcode.db import get_es
from findthatpostcode.settings import DEBUG

PCON_NAMES_AND_CODES_URL = "https://opendata.arcgis.com/api/v3/datasets/9a876e4777bc47e392e670a7b8bc3f5c_0/downloads/data?format=csv&spatialRefId=4326&where=1%3D1"
PCON_2010_LOOKUP_URL = "https://opendata.arcgis.com/api/v3/datasets/c776b66c0e534b849cae5a5121b7a16a_0/downloads/data?format=csv&spatialRefId=4326&where=1%3D1"
PCON_POSTCODE_URL = "https://www.arcgis.com/sharing/rest/content/items/f60c78533aa7462cb934bb4a81afc1e0/data"
PCON_BOUNDARIES_URL = "https://stg-arcgisazurecdataprod1.az.arcgis.com/exportfiles-1559-23529/Westminster_Parliamentary_Constituencies_July_2024_Boundaries_UK_BSC_7275719608364942765.geojson"


@click.command("new_pcon")
@click.option("--area-index", default=AREA_INDEX)
@click.option("--postcode-index", default=PC_INDEX)
def import_new_pcon(area_index=AREA_INDEX, postcode_index=PC_INDEX):
    if DEBUG:
        requests_cache.install_cache()

    es = get_es()

    # get the names and codes for the new areas
    r = requests.get(PCON_NAMES_AND_CODES_URL, stream=True)
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), "utf-8-sig"))
    areas = {}
    for row in reader:
        names = [row["PCON24NM"]]
        if row["PCON24NMW"]:
            names.append(row["PCON24NMW"])
        areas[row["PCON24CD"]] = {
            "code": row["PCON24CD"],
            "name": row["PCON24NM"],
            "name_welsh": row["PCON24NMW"] if row["PCON24NMW"] else None,
            "statutory_instrument_id": "1230/2023",
            "statutory_instrument_title": "The Parliamentary Constituencies Order 2023",
            "date_start": "2024-07-05T00:00:00",
            "date_end": None,
            "parent": None,
            "entity": row["PCON24CD"][0:3],
            "owner": "LGBC",
            "active": True,
            "areaehect": None,
            "areachect": None,
            "areaihect": None,
            "arealhect": None,
            "sort_order": row["PCON24CD"],
            "predecessor": [],
            "successor": [],
            "equivalents": {},
            "type": "pcon",
            "alternative_names": names,
        }

    # get the lookup for the 2010 areas
    r = requests.get(PCON_2010_LOOKUP_URL, stream=True)
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), "utf-8-sig"))
    update_2010 = defaultdict(list)
    for row in reader:
        areas[row["PCON24CD"]]["predecessor"].append(row["PCON10CD"])
        update_2010[row["PCON10CD"]].append(row["PCON24CD"])

    # create new areas and update old areas
    to_update = [
        {
            "_index": area_index,
            "_type": "_doc",
            "_op_type": "update",
            "_id": area_id,
            "doc_as_upsert": True,
            "doc": area,
        }
        for area_id, area in areas.items()
    ] + [
        {
            "_index": area_index,
            "_type": "_doc",
            "_op_type": "update",
            "_id": area_id,
            "doc_as_upsert": True,
            "doc": {
                "active": False,
                "successor": successors,
                "date_end": "2024-07-05T00:00:00",
            },
        }
        for area_id, successors in update_2010.items()
    ]

    bulk_upload(to_update, es, area_index, "new parliamentary constituencies")

    # fetch postcode data
    r = requests.get(PCON_POSTCODE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    for f in z.namelist():
        if not f.endswith(".csv"):
            continue
        with z.open(f, "r") as infile:
            reader = csv.DictReader(io.TextIOWrapper(infile, encoding="Windows-1252"))
            postcode_updates = []
            for row in tqdm.tqdm(reader):
                postcode = row["pcd"]
                # convert to "pcds" format
                postcode = "%s %s" % (postcode[:-3].strip(), postcode[-3:])
                record = {
                    "_index": postcode_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": postcode,
                    "doc": {
                        "pcon": row["pconcd"],
                    },
                }
                postcode_updates.append(record)

            bulk_upload(postcode_updates, es, postcode_index, "postcodes")

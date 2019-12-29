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
from flask import Flask, current_app
from flask.cli import with_appcontext
import requests
import requests_cache
from elasticsearch.helpers import bulk
import tqdm

from .. import db

requests_cache.install_cache()

RGC_URL = 'https://www.arcgis.com/sharing/rest/content/items/eb68d7b8bafe48b68aac10619c087a48/data'
CHD_URL = 'https://www.arcgis.com/sharing/rest/content/items/56b8f6d2d26646cb9d21fadca2f09452/data'
MSOA_URL = 'https://visual.parliament.uk/msoanames/static/MSOA-Names-v1.0.0.csv'
ENTITY_INDEX = 'geo_entity'
AREA_INDEX = 'geo_area'

def process_date(value, date_format='%d/%m/%Y'):
    if value in ['', 'n/a']:
        return None
    return datetime.datetime.strptime(value, date_format)

def process_int(value):
    if value in ['', 'n/a']:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return int(value)

def process_float(value):
    if value in ['', 'n/a']:
        return None
    if not isinstance(value, str):
        return value
    value = value.replace(",", "")
    return float(value)

@click.command('rgc')
@click.option('--url', default=RGC_URL)
@click.option('--es-index', default=ENTITY_INDEX)
@with_appcontext
def import_rgc(url=RGC_URL, es_index=ENTITY_INDEX):

    es = db.get_db()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    for f in z.namelist():
        if not f.endswith(".csv"):
            continue
        with z.open(f, 'r') as infile:
            reader = csv.DictReader(io.TextIOWrapper(infile, 'utf-8-sig'))
            entities = []
            for entity in reader:
                
                # tidy up a couple of records
                entity["Related entity codes"] = entity["Related entity codes"].replace("n/a", "").split(", ")

                entities.append({
                    "_index": es_index,
                    "_type": "_doc",
                    "_op_type": "update",
                    "_id": entity["Entity code"],
                    "doc_as_upsert": True,
                    "doc": {
                        "code": entity['Entity code'],
                        "name": entity['Entity name'],
                        "abbreviation": entity['Entity abbreviation'],
                        "theme": entity['Entity theme'],
                        "coverage": entity['Entity coverage'],
                        "related_codes": entity['Related entity codes'],
                        "status": entity['Status'],
                        "live_instances": process_int(entity['Number of live instances']),
                        "archived_instances": process_int(entity['Number of archived instances']),
                        "crossborder_instances": process_int(entity['Number of cross-border instances']),
                        "last_modified": process_date(entity['Date of last instance change']),
                        "current_code_first": entity['Current code (first in range)'],
                        "current_code_last": entity['Current code (last in range)'],
                        "reserved_code": entity['Reserved code (for CHD use)'],
                        "owner": entity['Entity owner'],
                        "date_introduced": process_date(entity['Date entity introduced on RGC']),
                        "date_start": process_date(entity['Entity start date']),
                    },
                })
            
            print("[entities] Processed %s entities" % len(entities))
            print("[elasticsearch] %s entities to save" % len(entities))
            results = bulk(es, entities)
            print("[elasticsearch] saved %s entities to %s index" % (results[0], es_index))
            print("[elasticsearch] %s errors reported" % len(results[1]))

@click.command('chd')
@click.option('--url', default=CHD_URL)
@click.option('--es-index', default=AREA_INDEX)
@with_appcontext
def import_chd(url=CHD_URL, es_index=AREA_INDEX):

    es = db.get_db()

    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    areas = {}

    with z.open('ChangeHistory.csv', 'r') as infile:
        click.echo('Opening {}'.format(infile.name))
        reader = csv.DictReader(io.TextIOWrapper(infile, 'utf-8-sig'))
        for k, area in tqdm.tqdm(enumerate(reader)):
            areas[area["GEOGCD"]] = {
                "_index": es_index,
                "_type": "_doc",
                "_op_type": "update",
                "_id": area["GEOGCD"],
                "doc_as_upsert": True,
                "doc": {
                    "code": area["GEOGCD"],
                    "name": area["GEOGNM"],
                    "name_welsh": area["GEOGNMW"] if area['GEOGNMW'] else None,
                    "statutory_instrument_id": area["SI_ID"] if area['SI_ID'] else None,
                    "statutory_instrument_title": area["SI_TITLE"] if area['SI_TITLE'] else None,
                    "date_start": process_date(area["OPER_DATE"], '%d/%m/%Y %H:%M:%S'),
                    "date_end": process_date(area["TERM_DATE"], '%d/%m/%Y %H:%M:%S'),
                    "parent": area["PARENTCD"] if area["PARENTCD"] else None,
                    "entity": area["ENTITYCD"],
                    "owner": area["OWNER"],
                    "active": area["STATUS"]=='live',
                    "areaehect": process_float(area["AREAEHECT"]),
                    "areachect": process_float(area["AREACHECT"]),
                    "areaihect": process_float(area["AREAIHECT"]),
                    "arealhect": process_float(area["AREALHECT"]),
                    "sort_order": area["GEOGCD"],
                    "predecessor": [],
                    "successor": [],
                    "equivalents": {},
                    # "type": area[""],
                }
            }

    with z.open('Changes.csv', 'r') as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, 'utf-8-sig'))
        click.echo('Opening {}'.format(infile.name))
        for k, area in tqdm.tqdm(enumerate(reader)):
            if area['GEOGCD_P']=='':
                continue
            if area['GEOGCD'] in areas:
                areas[area['GEOGCD']]["doc"]["predecessor"].append(area['GEOGCD_P'])
            if area['GEOGCD_P'] in areas:
                areas[area['GEOGCD_P']]["doc"]["successor"].append(area['GEOGCD'])

    equiv = {
        "ons": ["GEOGCDO", "GEOGNMO"],
        "mhclg": ["GEOGCDD", "GEOGNMD"],
        "nhs": ["GEOGCDH", "GEOGNMH"],
        "scottish_government": ["GEOGCDS", "GEOGNMS"],
        "welsh_government": ["GEOGCDWG", "GEOGNMWG", "GEOGNMWWG"],
    }
    with z.open('Equivalents.csv', 'r') as infile:
        reader = csv.DictReader(io.TextIOWrapper(infile, 'utf-8-sig'))
        click.echo('Opening {}'.format(infile.name))
        for area in tqdm.tqdm(reader):
            if area['GEOGCD'] not in areas:
                continue
            for k, v in equiv.items():
                if area[v[0]]:
                    areas[area['GEOGCD']]["doc"]["equivalents"][k] = area[v[0]]

    print("[areas] Processed %s areas" % len(areas))
    print("[elasticsearch] %s areas to save" % len(areas))
    results = bulk(es, areas.values())
    print("[elasticsearch] saved %s areas to %s index" % (results[0], es_index))
    print("[elasticsearch] %s errors reported" % len(results[1]))

@click.command('msoanames')
@click.option('--url', default=MSOA_URL)
@click.option('--es-index', default=AREA_INDEX)
@with_appcontext
def import_msoa_names(url=MSOA_URL, es_index=AREA_INDEX):

    es = db.get_db()

    r = requests.get(url, stream=True)
    
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8-sig'))
    area_updates = []
    for k, area in tqdm.tqdm(enumerate(reader)):
        new_doc = {
            "doc" : {
                "name" : area['msoa11hclnm'],
                "name_welsh": area['msoa11hclnmw'] if area['msoa11hclnmw'] else None
            }
        }
        area_updates.append({
            "_index": es_index,
            "_type": "_doc",
            "_op_type": "update",
            "_id": area["msoa11cd"],
            **new_doc
        })

    print("[areas] Processed %s areas" % len(area_updates))
    print("[elasticsearch] %s areas to save" % len(area_updates))
    results = bulk(es, area_updates)
    print("[elasticsearch] saved %s areas to %s index" % (results[0], es_index))
    print("[elasticsearch] %s errors reported" % len(results[1]))
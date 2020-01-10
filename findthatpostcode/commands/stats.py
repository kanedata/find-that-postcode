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
from .codes import AREA_INDEX

IMD2019_URL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/845345/File_7_-_All_IoD2019_Scores__Ranks__Deciles_and_Population_Denominators_3.csv'
IMD2015_URL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/467774/File_7_ID_2015_All_ranks__deciles_and_scores_for_the_Indices_of_Deprivation__and_population_denominators.csv'

def parse_field(k, v):
    if not isinstance(v, str):
        return v
    if v == '':
        return None
    if k.endswith("_decile") or k.endswith("_rank") or k.startswith("population_"):
        return int(v.split(".")[0])
    if k.endswith("_score"):
        return float(v)
    return v

IMD_FIELDS = {
    "LSOA code (2011)": "lsoa_code",
    "LSOA name (2011)": "lsoa_name",
    "Local Authority District code (2019)": "la_code",
    "Local Authority District name (2019)": "la_name",
    "Local Authority District code (2013)": "la_code",
    "Local Authority District name (2013)": "la_name",
    "Index of Multiple Deprivation (IMD) Score": "imd_score",
    "Index of Multiple Deprivation (IMD) Rank (where 1 is most deprived)": "imd_rank",
    "Index of Multiple Deprivation (IMD) Decile (where 1 is most deprived 10% of LSOAs)": "imd_decile",
    "Income Score (rate)": "imd_income_score",
    "Income Rank (where 1 is most deprived)": "imd_income_rank",
    "Income Decile (where 1 is most deprived 10% of LSOAs)": "imd_income_decile",
    "Employment Score (rate)": "imd_employment_score",
    "Employment Rank (where 1 is most deprived)": "imd_employment_rank",
    "Employment Decile (where 1 is most deprived 10% of LSOAs)": "imd_employment_decile",
    "Education, Skills and Training Score": "imd_education_score",
    "Education, Skills and Training Rank (where 1 is most deprived)": "imd_education_rank",
    "Education, Skills and Training Decile (where 1 is most deprived 10% of LSOAs)": "imd_education_decile",
    "Health Deprivation and Disability Score": "imd_health_score",
    "Health Deprivation and Disability Rank (where 1 is most deprived)": "imd_health_rank",
    "Health Deprivation and Disability Decile (where 1 is most deprived 10% of LSOAs)": "imd_health_decile",
    "Crime Score": "imd_crime_score",
    "Crime Rank (where 1 is most deprived)": "imd_crime_rank",
    "Crime Decile (where 1 is most deprived 10% of LSOAs)": "imd_crime_decile",
    "Barriers to Housing and Services Score": "imd_housing_score",
    "Barriers to Housing and Services Rank (where 1 is most deprived)": "imd_housing_rank",
    "Barriers to Housing and Services Decile (where 1 is most deprived 10% of LSOAs)": "imd_housing_decile",
    "Living Environment Score": "imd_environment_score",
    "Living Environment Rank (where 1 is most deprived)": "imd_environment_rank",
    "Living Environment Decile (where 1 is most deprived 10% of LSOAs)": "imd_environment_decile",
    "Income Deprivation Affecting Children Index (IDACI) Score (rate)": "idaci_score",
    "Income Deprivation Affecting Children Index (IDACI) Rank (where 1 is most deprived)": "idaci_rank",
    "Income Deprivation Affecting Children Index (IDACI) Decile (where 1 is most deprived 10% of LSOAs)": "idaci_decile",
    "Income Deprivation Affecting Older People (IDAOPI) Score (rate)": "idaopi_score",
    "Income Deprivation Affecting Older People (IDAOPI) Rank (where 1 is most deprived)": "idaopi_rank",
    "Income Deprivation Affecting Older People (IDAOPI) Decile (where 1 is most deprived 10% of LSOAs)": "idaopi_decile",
    "Children and Young People Sub-domain Score": "imd_education_children_score",
    "Children and Young People Sub-domain Rank (where 1 is most deprived)": "imd_education_children_rank",
    "Children and Young People Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_education_children_decile",
    "Adult Skills Sub-domain Score": "imd_education_adults_score",
    "Adult Skills Sub-domain Rank (where 1 is most deprived)": "imd_education_adults_rank",
    "Adult Skills Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_education_adults_decile",
    "Geographical Barriers Sub-domain Score": "imd_housing_geographical_score",
    "Geographical Barriers Sub-domain Rank (where 1 is most deprived)": "imd_housing_geographical_rank",
    "Geographical Barriers Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_housing_geographical_decile",
    "Wider Barriers Sub-domain Score": "imd_housing_wider_score",
    "Wider Barriers Sub-domain Rank (where 1 is most deprived)": "imd_housing_wider_rank",
    "Wider Barriers Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_housing_wider_decile",
    "Indoors Sub-domain Score": "imd_environment_indoors_score",
    "Indoors Sub-domain Rank (where 1 is most deprived)": "imd_environment_indoors_rank",
    "Indoors Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_environment_indoors_decile",
    "Outdoors Sub-domain Score": "imd_environment_outdoors_score",
    "Outdoors Sub-domain Rank (where 1 is most deprived)": "imd_environment_outdoors_rank",
    "Outdoors Sub-domain Decile (where 1 is most deprived 10% of LSOAs)": "imd_environment_outdoors_rank",
    "Total population: mid 2015 (excluding prisoners)": "population_total",
    "Dependent Children aged 0-15: mid 2015 (excluding prisoners)": "population_0_15",
    "Population aged 16-59: mid 2015 (excluding prisoners)": "population_16_59",
    "Older population aged 60 and over: mid 2015 (excluding prisoners)": "population_60_plus",
    "Total population: mid 2012 (excluding prisoners)": "population_total",
    "Dependent Children aged 0-15: mid 2012 (excluding prisoners)": "population_0_15",
    "Population aged 16-59: mid 2012 (excluding prisoners)": "population_16_59",
    "Older population aged 60 and over: mid 2012 (excluding prisoners)": "population_60_plus",
    "Working age population 18-59/64: for use with Employment Deprivation Domain (excluding prisoners)": "population_workingage",
}

@click.command('imd2019')
@click.option('--es-index', default=AREA_INDEX)
@click.option('--url', default=IMD2019_URL)
@with_appcontext
def import_imd2019(url=IMD2019_URL, es_index=AREA_INDEX):

    if current_app.config["DEBUG"]:
        requests_cache.install_cache()

    es = db.get_db()

    r = requests.get(url, stream=True)
    
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8-sig'))
    area_updates = []
    for k, area in tqdm.tqdm(enumerate(reader)):
        area = {IMD_FIELDS.get(k.strip(), k.strip()): parse_field(IMD_FIELDS.get(k.strip(), k.strip()), v) for k, v in area.items()}
        area_update = {
            "_index": es_index,
            "_type": "_doc",
            "_op_type": "update",
            "_id": area["lsoa_code"],
            "doc": {
                "stats": {
                    "imd2019": {k: v for k, v in area.items() if k.startswith("imd_")},
                    "idaci2019": {k: v for k, v in area.items() if k.startswith("idaci_")},
                    "idaopi2019": {k: v for k, v in area.items() if k.startswith("idaopi_")},
                    "population2015": {k: v for k, v in area.items() if k.startswith("population_")},
                }
            }
        }
        area_updates.append(area_update)

    print("[imd2019] Processed %s areas" % len(area_updates))
    print("[elasticsearch] %s areas to save" % len(area_updates))
    results = bulk(es, area_updates)
    print("[elasticsearch] saved %s areas to %s index" % (results[0], es_index))
    print("[elasticsearch] %s errors reported" % len(results[1]))

@click.command('imd2015')
@click.option('--es-index', default=AREA_INDEX)
@click.option('--url', default=IMD2015_URL)
@with_appcontext
def import_imd2015(url=IMD2015_URL, es_index=AREA_INDEX):

    if current_app.config["DEBUG"]:
        requests_cache.install_cache()

    es = db.get_db()

    r = requests.get(url, stream=True)
    
    reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8-sig'))
    area_updates = []
    for k, area in tqdm.tqdm(enumerate(reader)):
        area = {IMD_FIELDS.get(k.strip(), k.strip()): parse_field(IMD_FIELDS.get(k.strip(), k.strip()), v) for k, v in area.items()}
        area_update = {
            "_index": es_index,
            "_type": "_doc",
            "_op_type": "update",
            "_id": area["lsoa_code"],
            "doc": {
                "stats": {
                    "imd2015": {k: v for k, v in area.items() if k.startswith("imd_")},
                    "idaci2015": {k: v for k, v in area.items() if k.startswith("idaci_")},
                    "idaopi2015": {k: v for k, v in area.items() if k.startswith("idaopi_")},
                    "population2012": {k: v for k, v in area.items() if k.startswith("population_")},
                }
            }
        }
        area_updates.append(area_update)

    print("[imd2015] Processed %s areas" % len(area_updates))
    print("[elasticsearch] %s areas to save" % len(area_updates))
    results = bulk(es, area_updates)
    print("[elasticsearch] saved %s areas to %s index" % (results[0], es_index))
    print("[elasticsearch] %s errors reported" % len(results[1]))

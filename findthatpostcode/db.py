import datetime
from typing import Annotated, Any

import click
from boto3 import session
from elasticsearch import Elasticsearch
from fastapi import Depends
from sqlite_utils import Database

from findthatpostcode.settings import (
    ES_URL,
    LOGGING_DB,
    S3_ACCESS_ID,
    S3_ENDPOINT,
    S3_REGION,
    S3_SECRET_KEY,
)

INDEXES = {
    "geo_postcode": {
        "properties": {
            "location": {"type": "geo_point"},
            "hash": {"type": "text", "index_prefixes": {}},
        }
    },
    "geo_placename": {"properties": {"location": {"type": "geo_point"}}},
    "geo_area": {"properties": {"boundary": {"type": "geo_shape"}}},
}


async def get_es():
    db = Elasticsearch(ES_URL)
    try:
        yield db
    finally:
        db.close()


ElasticsearchDep = Annotated[Elasticsearch, Depends(get_es)]


def init_db(es: Elasticsearch, reset=False):
    doc_type = "_doc"

    for index, mapping in INDEXES.items():
        if es.indices.exists(index) and reset:
            click.echo("[elasticsearch] deleting '%s' index..." % (index))
            res = es.indices.delete(index=index)
            click.echo("[elasticsearch] response: '%s'" % (res))
        click.echo("[elasticsearch] creating '%s' index..." % (index))
        res = es.indices.create(index=index)

        res = es.indices.put_mapping(
            doc_type=doc_type, body=mapping, index=index, include_type_name=True
        )
        click.echo(
            "[elasticsearch] set mapping on %s index, %s type" % (index, doc_type)
        )


async def get_log_db():
    if LOGGING_DB:
        datetime.datetime.now()
        db = Database(
            LOGGING_DB.format(
                year=datetime.datetime.now().year,
                month=datetime.datetime.now().month,
                day=datetime.datetime.now().day,
            )
        )
    else:
        db = Database(memory=True)
    try:
        yield db
    finally:
        db.close()


LogDatabaseDep = Annotated[Database, Depends(get_log_db)]


def get_s3_client():
    s3_session = session.Session()
    return s3_session.client(
        "s3",
        region_name=S3_REGION,
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_ID,
        aws_secret_access_key=S3_SECRET_KEY,
    )


S3Dep = Annotated[Any, Depends(get_s3_client)]


@click.command("init-db")
@click.option("--reset/--no-reset", default=False)
def init_db_command(reset):
    """Clear the existing data and create new tables."""
    init_db(reset)
    click.echo("Initialized the database.")

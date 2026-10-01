import datetime as dt

import click
from boto3 import session
from elasticsearch import Elasticsearch
from flask import current_app, g
from flask.cli import with_appcontext
from sqlite_utils import Database

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


def get_db():
    if "db" not in g:
        g.db = Elasticsearch(current_app.config["ES_URL"])

    return g.db


def close_db(e=None):
    g.pop("db", None)


def init_db(reset=False):
    es = get_db()
    doc_type = "_doc"

    for index, mapping in INDEXES.items():
        if es.indices.exists(index) and reset:
            click.echo(f"[elasticsearch] deleting '{index}' index...")
            res = es.indices.delete(index=index)
            click.echo(f"[elasticsearch] response: '{res}'")
        click.echo(f"[elasticsearch] creating '{index}' index...")
        res = es.indices.create(index=index)

        res = es.indices.put_mapping(
            doc_type=doc_type, body=mapping, index=index, include_type_name=True
        )
        click.echo(f"[elasticsearch] set mapping on {index} index, {doc_type} type")


def get_log_db():
    if "log_db" not in g:
        if current_app.config.get("LOGGING_DB"):
            dt.datetime.now(dt.timezone.utc)
            g.log_db = Database(
                current_app.config.get("LOGGING_DB").format(
                    year=dt.datetime.now(dt.timezone.utc).year,
                    month=dt.datetime.now(dt.timezone.utc).month,
                    day=dt.datetime.now(dt.timezone.utc).day,
                )
            )
        else:
            g.log_db = Database(memory=True)

    return g.log_db


def close_log_db(e=None):
    if "log_db" in g:
        g.log_db.close()
        g.pop("log_db", None)


def get_s3_client():
    if "s3_client" not in g:
        s3_session = session.Session()
        g.s3_client = s3_session.client(
            "s3",
            region_name=current_app.config["S3_REGION"],
            endpoint_url=current_app.config["S3_ENDPOINT"],
            aws_access_key_id=current_app.config["S3_ACCESS_ID"],
            aws_secret_access_key=current_app.config["S3_SECRET_KEY"],
        )
    return g.s3_client


def close_s3_client(e=None):
    if "s3_client" in g:
        g.s3_client.close()
        g.pop("s3_client", None)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_log_db)
    app.teardown_appcontext(close_s3_client)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@click.option("--reset/--no-reset", default=False)
@with_appcontext
def init_db_command(reset):
    """Clear the existing data and create new tables."""
    init_db(reset)
    click.echo("Initialized the database.")

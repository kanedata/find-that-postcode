import datetime

import click
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


def get_log_db():
    if "log_db" not in g:
        if current_app.config.get("LOGGING_DB"):
            now = datetime.datetime.now()
            g.log_db = Database(
                current_app.config.get("LOGGING_DB").format(
                    year=datetime.datetime.now().year,
                    month=datetime.datetime.now().month,
                    day=datetime.datetime.now().day,
                )
            )
        else:
            g.log_db = Database(memory=True)

    return g.log_db


def close_log_db(e=None):
    if "log_db" in g:
        g.log_db.close()
        g.pop("log_db", None)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.teardown_appcontext(close_log_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@click.option("--reset/--no-reset", default=False)
@with_appcontext
def init_db_command(reset):
    """Clear the existing data and create new tables."""
    init_db(reset)
    click.echo("Initialized the database.")

from elasticsearch import Elasticsearch

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = Elasticsearch(current_app.config['ES_URL'])

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

def init_db():
    db = get_db()
    # @TODO: create elasticsearch index mappings here


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
import os
import datetime

from flask import Flask, render_template
from flask_cors import CORS

from . import db
from . import commands
from . import blueprints
from .metadata import KEY_AREA_TYPES, OTHER_CODES, AREA_TYPES
from .controllers.areatypes import area_types_count


def get_es_url(default):

    potential_env_vars = [
        "ELASTICSEARCH_URL",
        "ES_URL",
        "BONSAI_URL"
    ]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            return os.environ.get(e_v)
    return default


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        ES_URL=get_es_url('http://localhost:9200'),
        ES_INDEX=os.environ.get('ES_INDEX', 'postcodes'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    commands.init_app(app)
    CORS(app)

    # template helpers
    @app.context_processor
    def inject_now():
        return dict(
            now=datetime.datetime.now(),
            key_area_types=KEY_AREA_TYPES,
            other_codes=OTHER_CODES,
            area_types=AREA_TYPES,
        )

    # routes and blueprints
    @app.route('/')
    def index():
        ats = area_types_count(db.get_db())
        return render_template('index.html.j2', result=ats)

    @app.route('/about')
    def about():
        return render_template('about.html.j2')

    blueprints.init_app(app)

    return app

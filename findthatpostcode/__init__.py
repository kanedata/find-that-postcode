import datetime
import os
import re

import sentry_sdk
from flask import Flask, make_response, render_template
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from findthatpostcode import blueprints, commands, db
from findthatpostcode.controllers.areas import area_types_count
from findthatpostcode.metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES


def get_es_url(default):
    potential_env_vars = ["ELASTICSEARCH_URL", "ES_URL", "BONSAI_URL"]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            return os.environ.get(e_v)
    return default


def create_app(test_config=None):
    if os.environ.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            integrations=[FlaskIntegration()],
            environment=(
                "development" if os.environ.get("FLASK_DEBUG") else "production"
            ),
            traces_sample_rate=0.005,
            profiles_sample_rate=0.005,
        )

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        ES_URL=get_es_url("http://localhost:9200"),
        ES_INDEX=os.environ.get("ES_INDEX", "postcodes"),
        LOGGING_DB=os.environ.get("LOGGING_DB"),
        SERVER_NAME=os.environ.get("SERVER_NAME"),
        S3_REGION=os.environ.get("S3_REGION"),
        S3_ENDPOINT=os.environ.get("S3_ENDPOINT"),
        S3_ACCESS_ID=os.environ.get("S3_ACCESS_ID"),
        S3_SECRET_KEY=os.environ.get("S3_SECRET_KEY"),
        S3_BUCKET=os.environ.get("S3_BUCKET", "geo-boundaries"),
        ETHICAL_ADS_PUBLISHER=os.environ.get("ETHICAL_ADS_PUBLISHER"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
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
            ethical_ads_publisher=app.config.get("ETHICAL_ADS_PUBLISHER"),
        )

    @app.template_filter()
    def expand_commas(s):
        if not isinstance(s, str):
            return s
        return re.sub(r"\b,\b", ", ", s)

    # routes and blueprints
    @app.route("/")
    def index():
        ats = area_types_count(db.get_db())
        return render_template("index.html.j2", result=ats)

    @app.route("/robots.txt")
    def robots():
        text = render_template("robots.txt")
        response = make_response(text)
        response.headers["Content-Type"] = "text/plain"
        return response

    @app.route("/about")
    def about():
        return render_template("about.html.j2")

    blueprints.init_app(app)

    return app

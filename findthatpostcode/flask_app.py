import datetime
import os
import re

import sentry_sdk
from flask import Flask, make_response, render_template
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration

from findthatpostcode import blueprints, commands, db, settings
from findthatpostcode.controllers.areas import area_types_count
from findthatpostcode.metadata import (
    AREA_TYPES,
    KEY_AREA_TYPES,
    OTHER_CODES,
    STATS_FIELDS,
)


def create_app(test_config=None):
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            environment=settings.ENVIRONMENT,
            traces_sample_rate=0.005,
            profiles_sample_rate=0.005,
        )

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=settings.SECRET_KEY,
        ES_URL=settings.ES_URL,
        ES_INDEX=settings.ES_INDEX,
        LOGGING_DB=settings.LOGGING_DB,
        SERVER_NAME=settings.SERVER_NAME,
        S3_REGION=settings.S3_REGION,
        S3_ENDPOINT=settings.S3_ENDPOINT,
        S3_ACCESS_ID=settings.S3_ACCESS_ID,
        S3_SECRET_KEY=settings.S3_SECRET_KEY,
        S3_BUCKET=settings.S3_BUCKET,
        ETHICAL_ADS_PUBLISHER=settings.ETHICAL_ADS_PUBLISHER,
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
            stats_fields=STATS_FIELDS,
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

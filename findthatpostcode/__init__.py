import datetime
import os
import re

from flask import Flask, make_response, render_template, render_template_string, request
from flask_cors import CORS
from ua_parser import user_agent_parser

from findthatpostcode import blueprints, commands, db
from findthatpostcode.controllers.areatypes import area_types_count
from findthatpostcode.metadata import AREA_TYPES, KEY_AREA_TYPES, OTHER_CODES


def get_es_url(default):

    potential_env_vars = ["ELASTICSEARCH_URL", "ES_URL", "BONSAI_URL"]
    for e_v in potential_env_vars:
        if os.environ.get(e_v):
            return os.environ.get(e_v)
    return default


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        ES_URL=get_es_url("http://localhost:9200"),
        ES_INDEX=os.environ.get("ES_INDEX", "postcodes"),
        LOGGING_DB=os.environ.get("LOGGING_DB"),
        SERVER_NAME=os.environ.get("SERVER_NAME"),
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

    @app.after_request
    def request_log(response):
        ua = user_agent_parser.Parse(request.user_agent.string)
        if request.endpoint == "static":
            return response
        db.get_log_db()["logs"].insert(
            {
                "app": "findthatpostcode",
                "timestamp": datetime.datetime.now().isoformat(),
                "url": request.url,
                "path": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "origin": request.origin,
                "referrer": request.referrer,
                # "remote_addr": request.remote_addr,  # we don't collect IP address
                "endpoint": request.endpoint,
                "view_args": request.view_args,
                "user_agent_string": ua.get("string") if ua else None,
                "user_agent": {k: v for k, v in ua.items() if k != "string"}
                if ua
                else None,
                "status_code": response.status_code,
                "response_size": response.content_length,
                "content_type": response.mimetype,
            },
        )
        db.close_log_db()
        return response

    return app

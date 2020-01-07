import os
import datetime

from flask import Flask, render_template
from . import db
from . import commands
from . import blueprints
from .metadata import KEY_AREA_TYPES, OTHER_CODES, AREA_TYPES
from .controllers.areatypes import area_types_count

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        ES_URL=os.environ.get('ES_URL', 'http://localhost:9200'),
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
    @app.route('/index.html')
    def index():
        ats = area_types_count(db.get_db())
        return render_template('index.html', result=ats)
    
    blueprints.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
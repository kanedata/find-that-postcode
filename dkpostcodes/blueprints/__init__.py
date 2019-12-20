from . import areas
from . import postcodes

def init_app(app):

    app.register_blueprint(areas.bp)
    app.register_blueprint(postcodes.bp)

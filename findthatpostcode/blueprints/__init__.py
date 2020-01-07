from . import areas
from . import postcodes
from . import reconcile

def init_app(app):

    app.register_blueprint(areas.bp)
    app.register_blueprint(postcodes.bp)
    app.register_blueprint(reconcile.bp)

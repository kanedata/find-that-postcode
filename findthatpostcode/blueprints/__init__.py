from . import areas
from . import areatypes
from . import postcodes
from . import points
from . import places
from . import reconcile
from . import addtocsv
from . import search


def init_app(app):

    app.register_blueprint(areas.bp)
    app.register_blueprint(areatypes.bp)
    app.register_blueprint(postcodes.bp)
    app.register_blueprint(points.bp)
    app.register_blueprint(reconcile.bp)
    app.register_blueprint(addtocsv.bp)
    app.register_blueprint(places.bp)
    app.register_blueprint(search.bp)

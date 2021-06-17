from . import (
    addtocsv,
    areas,
    areatypes,
    places,
    points,
    postcodes,
    reconcile,
    search,
    tools,
)


def init_app(app):

    app.register_blueprint(areas.bp)
    app.register_blueprint(areatypes.bp)
    app.register_blueprint(postcodes.bp)
    app.register_blueprint(points.bp)
    app.register_blueprint(reconcile.bp)
    app.register_blueprint(addtocsv.bp)
    app.register_blueprint(places.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(tools.bp)

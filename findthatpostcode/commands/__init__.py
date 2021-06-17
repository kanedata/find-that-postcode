from flask.cli import AppGroup

from . import boundaries, codes, placenames, postcodes, stats


def init_app(app):

    import_cli = AppGroup("import")
    import_cli.add_command(codes.import_chd)
    import_cli.add_command(codes.import_rgc)
    import_cli.add_command(codes.import_msoa_names)
    import_cli.add_command(boundaries.import_boundaries)
    import_cli.add_command(postcodes.import_nspl)
    import_cli.add_command(stats.import_imd2019)
    import_cli.add_command(stats.import_imd2015)
    import_cli.add_command(placenames.import_placenames)

    app.cli.add_command(import_cli)

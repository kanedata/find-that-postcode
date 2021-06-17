from flask import Blueprint, make_response, render_template, request

bp = Blueprint("tools", __name__, url_prefix="/tools")


@bp.route("/merge-geojson", strict_slashes=False, methods=["GET"])
def merge_geojson():
    return render_template("merge-geojson.html.j2")

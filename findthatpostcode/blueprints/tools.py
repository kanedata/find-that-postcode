from flask import Blueprint, render_template

bp = Blueprint("tools", __name__, url_prefix="/tools")


@bp.route("/merge-geojson", strict_slashes=False, methods=["GET"])
def merge_geojson():
    return render_template("merge-geojson.html.j2")


@bp.route("/reduce-geojson", strict_slashes=False, methods=["GET"])
def reduce_geojson():
    return render_template("reduce-geojson.html.j2")

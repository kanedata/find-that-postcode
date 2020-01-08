import tempfile
import os
import codecs

from flask import Blueprint, current_app, abort, jsonify, make_response, request, render_template

from .utils import return_result
from .process_csv import process_csv
from findthatpostcode.controllers.areatypes import area_types_count
from findthatpostcode.metadata import BASIC_UPLOAD_FIELDS, DEFAULT_UPLOAD_FIELDS
from findthatpostcode.db import get_db

bp = Blueprint('addtocsv', __name__, url_prefix='/addtocsv')


@bp.route('/', strict_slashes=False, methods=['GET'])
def addtocsv():
    ats = area_types_count(get_db())
    return render_template(
        'addtocsv.html',
        result=ats,
        basic_fields=BASIC_UPLOAD_FIELDS,
        default_fields=DEFAULT_UPLOAD_FIELDS
    )


@bp.route('/', strict_slashes=False, methods=['POST'])
def return_csv():
    upload = request.files.get('csvfile')
    column_name = request.form.get("column_name", "postcode")
    fields = request.form.getlist("fields")
    if not fields:
        fields = DEFAULT_UPLOAD_FIELDS

    if "latlng" in fields:
        fields.append("lat")
        fields.append("long")
        fields.remove("latlng")

    if "estnrth" in fields:
        fields.append("oseast1m")
        fields.append("osnrth1m")
        fields.remove("estnrth")

    if "lep" in fields:
        fields.append("lep1")
        fields.append("lep2")
        fields.remove("lep")

    if "lep_name" in fields:
        fields.append("lep1_name")
        fields.append("lep2_name")
        fields.remove("lep_name")

    _, ext = os.path.splitext(upload.filename)
    if ext not in ['.csv']:
        return 'File extension not allowed.'

    with tempfile.SpooledTemporaryFile(mode='w+', newline='') as output:
        process_csv(codecs.iterdecode(upload.stream, 'utf-8'), output, get_db(), column_name, fields)
        output.seek(0)

        response = make_response(output.read())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(upload.filename)
        return response

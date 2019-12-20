from flask import abort, make_response, jsonify, render_template

from dkpostcodes.metadata import KEY_AREA_TYPES, OTHER_CODES

def return_result(result, filetype="json", template=None):
    if filetype == "html" and not template:
        abort(500, "No template provided")

    status = 200 if result.found else 404

    if status != 200:
        errors = result.get_errors()
        if filetype in ("json", "geojson"):
            return abort(make_response(jsonify(message=result), status))
        elif filetype == "html":
            # @TODO: non-json response here
            return abort(make_response(jsonify(message=result), status))

    if filetype in ("json", "geojson"):
        return jsonify(result.topJSON())
    elif filetype == "html":
        return render_template(
            template,
            result=result,
        )

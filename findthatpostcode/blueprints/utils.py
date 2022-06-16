from functools import wraps

from flask import abort, current_app, jsonify, make_response, render_template, request


def return_result(result, filetype="json", template=None, **kwargs):
    if filetype == "html" and not template:
        abort(500, "No template provided")

    status = 200 if result.found else 404

    if status != 200:
        errors = result.get_errors()
        if errors and errors[0].get("status"):
            status = int(errors[0]["status"])
        if filetype in ("json", "geojson"):
            return abort(make_response(jsonify(message=result.topJSON()), status))
        elif filetype == "html":
            # @TODO: non-json response here
            return abort(
                make_response(
                    render_template(
                        "error.html.j2", result=result, errors=errors, **kwargs
                    ),
                    status,
                )
            )

    if filetype in ("json", "geojson"):
        return jsonify(result.topJSON())
    elif filetype == "html":
        return render_template(template, result=result, **kwargs)

    abort(404)


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get("callback", False)
        if callback:
            data = func(*args, **kwargs).data
            data = data.decode("utf8") if isinstance(data, bytes) else str(data)
            content = str(callback) + "(" + data + ")"
            mimetype = "application/javascript"
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)

    return decorated_function


def cors(func):
    """Adds cors headers for requests (allows all)."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        response = func(*args, **kwargs)
        response.headers[
            "Access-Control-Allow-Methods"
        ] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    return decorated_function

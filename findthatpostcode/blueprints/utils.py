from functools import wraps

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from findthatpostcode.utils import templates


def return_result(result, filetype="json", template=None, **kwargs):
    if filetype == "html" and not template:
        raise HTTPException(status_code=500, detail="No template provided")

    status = 200 if result.found else 404

    if status != 200:
        errors = result.get_errors()
        if errors and errors[0].get("status"):
            status = int(errors[0]["status"])
        if filetype in ("json", "geojson"):
            raise HTTPException(status_code=status, detail=result.topJSON())
        elif filetype == "html":
            return templates.TemplateResponse(
                "error.html.j2",
                {"result": result, "errors": errors, **kwargs},
                status_code=status,
            )

    if filetype in ("json", "geojson"):
        return JSONResponse(result.topJSON())
    elif filetype == "html":
        return templates.TemplateResponse(template, {"result": result, **kwargs})

    raise HTTPException(status_code=404, detail="Not found")


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
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
        )
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    return decorated_function

from fastapi import HTTPException, Request

from findthatpostcode.utils import templates


def return_result(
    result,
    request: Request = None,
    filetype: str = "json",
    template: str = None,
    **kwargs,
):
    if filetype == "html" and not template:
        raise HTTPException(status_code=500, detail="No template provided")
    if template and not request:
        raise HTTPException(
            status_code=500, detail="No request provided for HTML response"
        )

    status = 200 if result.found else 404

    if status != 200:
        errors = result.get_errors()
        if errors and errors[0].get("status"):
            status = int(errors[0]["status"])
        if filetype in ("json", "geojson"):
            raise HTTPException(status_code=status, detail=result.topJSON())
        elif filetype == "html":
            return templates.TemplateResponse(
                request=request,
                name="error.html.j2",
                context={"result": result, "errors": errors, **kwargs},
                status_code=status,
                media_type="text/html",
            )

    if filetype in ("json", "geojson"):
        return result.topJSON()
    elif filetype == "html":
        return templates.TemplateResponse(
            request=request,
            name=template,
            context={"result": result, **kwargs},
            media_type="text/html",
        )

    raise HTTPException(status_code=404, detail="Not found")

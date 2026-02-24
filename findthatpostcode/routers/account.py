from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

from findthatpostcode.crud.auth import authenticate_user, get_user
from findthatpostcode.db import DatabaseDep
from findthatpostcode.security import PwdContextDep
from findthatpostcode.utils import templates

router = APIRouter()


class LoginForm(BaseModel):
    email: str
    password: str
    csrf_token: str
    model_config = {"extra": "forbid"}


# @router.get("/", response_class=HTMLResponse)
@router.get("/")
async def show_account(
    request: Request,
    db: DatabaseDep,
):
    if "user_email" not in request.session:
        return RedirectResponse(url=request.url_for("login_page"), status_code=303)

    user = get_user(db, request.session["user_email"])
    if not user:
        del request.session["user_email"]
        return RedirectResponse(url=request.url_for("login_page"), status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="account.html.j2",
        context={"user": user},
        media_type="text/html",
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, csrf_protect: CsrfProtect = Depends()):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    response = templates.TemplateResponse(
        request=request,
        name="login.html.j2",
        context={"form": LoginForm, "csrf_token": csrf_token},
        media_type="text/html",
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


@router.post("/login", response_class=RedirectResponse)
async def login_submit(
    request: Request,
    data: Annotated[LoginForm, Form()],
    pwd_context: PwdContextDep,
    db: DatabaseDep,
    csrf_protect: CsrfProtect = Depends(),
):
    await csrf_protect.validate_csrf(request)
    user = authenticate_user(pwd_context, db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    response = RedirectResponse(
        url=request.url_for("show_account"),
        status_code=303,
    )
    csrf_protect.unset_csrf_cookie(response)  # prevent token reuse
    request.session["user_email"] = user.email
    return response

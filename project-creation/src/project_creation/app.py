"""FastAPI application factory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from project_creation.auth import AccountAuthenticator, SessionManager
from project_creation.config import Settings
from project_creation.repository import RunRepository

SESSION_COOKIE = "project_creation_session"


@dataclass(frozen=True, slots=True)
class AppServices:
    authenticator: AccountAuthenticator
    sessions: SessionManager


def create_app(
    settings: Settings,
    repository: RunRepository,
    services: AppServices,
) -> FastAPI:
    app = FastAPI(title="SSI Project Creation")
    app.state.settings = settings
    app.state.repository = repository
    app.state.services = services

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/login", response_class=HTMLResponse)
    def login_page() -> str:
        return (
            '<form method="post" action="/login">'
            '<input name="username" autocomplete="username">'
            '<input name="password" type="password" autocomplete="current-password">'
            "<button>Sign in</button>"
            "</form>"
        )

    @app.post("/login")
    def login(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ) -> Response:
        user = services.authenticator.authenticate(username, password)
        if user is None:
            return JSONResponse({"detail": "Invalid credentials"}, status_code=401)
        cookie = services.sessions.issue(user)
        response = RedirectResponse("/", status_code=303)
        response.set_cookie(
            SESSION_COOKIE,
            cookie,
            max_age=services.sessions.ttl_seconds,
            httponly=True,
            samesite="lax",
            secure=services.sessions.secure_cookie,
        )
        return response

    @app.get("/")
    def home(request: Request) -> Response:
        cookie = request.cookies.get(SESSION_COOKIE, "")
        session_user = services.sessions.verify(cookie)
        if session_user is None:
            return RedirectResponse("/login", status_code=303)
        user = services.authenticator.current_user(session_user.id)
        if user is None:
            return RedirectResponse("/login", status_code=303)
        return JSONResponse(
            {
                "username": user.username,
                "role": user.role,
                "csrf_token": services.sessions.csrf_token(cookie),
            }
        )

    @app.post("/logout")
    def logout(
        request: Request,
        csrf_token: Annotated[str, Form()],
    ) -> Response:
        cookie = request.cookies.get(SESSION_COOKIE, "")
        session_user = services.sessions.verify(cookie)
        if session_user is None:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        user = services.authenticator.current_user(session_user.id)
        if user is None:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)
        if not services.sessions.verify_csrf(cookie, csrf_token):
            return JSONResponse({"detail": "Invalid CSRF token"}, status_code=403)
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(SESSION_COOKIE)
        return response

    return app

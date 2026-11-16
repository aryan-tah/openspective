"""The HTTP server: Perspective's endpoints at Perspective's paths."""

from __future__ import annotations

import json
import secrets
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from openspective import __version__, errors
from openspective.backends import Backend, load
from openspective.discovery import document
from openspective.errors import ApiError
from openspective.language import LanguageDetector
from openspective.schema import AnalyzeCommentRequest, SuggestCommentScoreRequest
from openspective.service import Analyzer
from openspective.settings import Settings


def _check_key(request: Request, keys: frozenset[str]) -> None:
    if not keys:
        return
    supplied = request.query_params.get("key") or request.headers.get("x-goog-api-key") or ""
    if not any(secrets.compare_digest(supplied, k) for k in keys):
        raise errors.missing_key()


async def _body(request: Request) -> dict[str, Any]:
    raw = await request.body()
    try:
        data = json.loads(raw or b"{}")
    except ValueError:
        raise ApiError("Invalid JSON payload received.", error_type="INVALID_REQUEST") from None
    if not isinstance(data, dict):
        raise ApiError("Invalid JSON payload received: expected an object.", error_type="INVALID_REQUEST")
    return data


def create_app(settings: Settings | None = None, backend: Backend | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    backend = backend or load(settings.backend)
    preload = getattr(backend, "preload", None)
    if settings.preload and callable(preload):
        preload()
    analyzer = Analyzer(
        backend,
        LanguageDetector(fallback=settings.default_language),
        max_comment_bytes=settings.max_comment_bytes,
        feedback_path=settings.feedback_path,
    )
    app = FastAPI(
        title="openspective",
        version=__version__,
        description="Self-hosted, Perspective API compatible comment scoring.",
        docs_url="/docs",
        redoc_url=None,
    )
    app.state.analyzer = analyzer

    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(exc.body(), status_code=exc.code)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        err = ApiError(str(exc.detail), code=exc.status_code)
        return JSONResponse(err.body(), status_code=exc.status_code)

    @app.post("/v1alpha1/comments:analyze")
    async def analyze(request: Request) -> JSONResponse:
        _check_key(request, settings.api_keys)
        try:
            req = AnalyzeCommentRequest.model_validate(await _body(request))
        except ValueError as e:
            raise errors.invalid_request(f"Invalid request: {e}") from None
        result = await _run(analyzer.analyze, req)
        return JSONResponse(result.to_json())

    @app.post("/v1alpha1/comments:suggestscore")
    async def suggestscore(request: Request) -> JSONResponse:
        _check_key(request, settings.api_keys)
        try:
            req = SuggestCommentScoreRequest.model_validate(await _body(request))
        except ValueError as e:
            raise errors.invalid_request(f"Invalid request: {e}") from None
        result = await _run(analyzer.suggest, req)
        return JSONResponse(result.to_json())

    def _discovery(request: Request) -> JSONResponse:
        root = settings.public_url or str(request.base_url)
        return JSONResponse(document(root))

    app.add_api_route("/$discovery/rest", _discovery, methods=["GET"], include_in_schema=False)
    app.add_api_route(
        "/discovery/v1/apis/commentanalyzer/v1alpha1/rest",
        _discovery,
        methods=["GET"],
        include_in_schema=False,
    )

    @app.get("/v1alpha1/attributes")
    def supported() -> dict[str, Any]:
        """openspective extension: which attributes can be scored in which languages."""
        return {
            "backend": analyzer.backend.name,
            "attributes": {k: sorted(v) for k, v in sorted(analyzer.support.items())},
        }

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "backend": analyzer.backend.name}

    return app


async def _run(fn: Any, arg: Any) -> Any:
    """Model inference is CPU-bound; keep it off the event loop."""
    from starlette.concurrency import run_in_threadpool

    return await run_in_threadpool(fn, arg)

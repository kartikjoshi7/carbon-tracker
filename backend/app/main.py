"""
FastAPI application entry point.

Configures CORS, security headers, rate-limiting, and SPA serving.
"""
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore[import-untyped]
from slowapi.errors import RateLimitExceeded  # type: ignore[import-untyped]
from slowapi.util import get_remote_address  # type: ignore[import-untyped]

from app.routers import footprint

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Carbon Footprint Awareness Platform",
    description="API for calculating, tracking, and reducing personal carbon emissions.",
    version="1.0.0",
)
app.state.limiter = limiter  # type: ignore[attr-defined]
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# ── CORS ────────────────────────────────────────────────────────────
# Restrictive allow-list for local development origins only.
# In production (single container), the SPA is served from the same
# origin, so CORS is not triggered.

_ALLOWED_ORIGINS: list[str] = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Security Headers Middleware ─────────────────────────────────────

@app.middleware("http")
async def add_security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Inject hardened security headers into every HTTP response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# ── Health Check ────────────────────────────────────────────────────

@app.get("/api/health")
@limiter.limit("10/minute")
async def health_check(request: Request) -> dict[str, str]:
    """Liveness / readiness probe."""
    return {"status": "online", "message": "Server is operational"}


# ── Router Registration ────────────────────────────────────────────

app.include_router(footprint.router)


# ── SPA Serving ─────────────────────────────────────────────────────
# Serves the built React frontend (single-page app) when the static
# directory exists (i.e., inside the Docker container).

if os.path.isdir("static"):
    if os.path.isdir("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve the SPA for client-side routing; 404 for unknown API paths."""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")

        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        return FileResponse("static/index.html")


from fastapi import FastAPI, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from slowapi.util import get_remote_address  # type: ignore

from app.routers import footprint  # type: ignore

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Carbon Engine API")
app.state.limiter = limiter  # type: ignore
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):  # type: ignore
    """Inject hardened security headers into every HTTP response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


@app.get("/api/health")
@limiter.limit("10/minute")
async def health_check(request: Request) -> dict[str, str]:
    """
    Health check path.
    """
    return {"status": "online", "message": "Server is operational"}

# Include footprint router
app.include_router(footprint.router)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve the built React frontend (SPA) if the static directory exists
if os.path.isdir("static"):
    # Mount the assets folder directly
    if os.path.isdir("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
        
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Let FastAPI handle /api routes normally (they should 404 if not found)
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
            
        # Serve exact file if it exists (e.g., manifest.webmanifest, sw.js)
        file_path = os.path.join("static", full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Fallback to index.html for React Router client-side routing
        return FileResponse("static/index.html")

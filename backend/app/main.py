from typing import Dict
from app.routers import footprint  # type: ignore
from fastapi import FastAPI, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from slowapi import Limiter, _rate_limit_exceeded_handler  # type: ignore
from slowapi.errors import RateLimitExceeded  # type: ignore
from slowapi.util import get_remote_address  # type: ignore

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


@app.get("/")
@limiter.limit("10/minute")
async def health_check(request: Request) -> Dict[str, str]:
    """
    Root health check path.
    """
    return {"status": "online", "message": "Server is operational"}

# Include footprint router
app.include_router(footprint.router)

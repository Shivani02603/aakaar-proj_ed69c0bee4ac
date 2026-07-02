import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database.config import init_db
from backend.routers.auth import router as auth_router
from backend.routers.performance import router as performance_router
from backend.routers.reliability import router as reliability_router
from backend.routers.scalability import router as scalability_router
from backend.routers.security import router as security_router
from backend.routers.sessions import router as sessions_router
from backend.routers.usability import router as usability_router
from backend.routers.users import router as users_router

# Initialize FastAPI app
app = FastAPI(
    title="Aakaar Project API",
    description="API for Aakaar Project, providing endpoints for document management, chat sessions, and monitoring.",
    version="1.0.0",
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"detail": str(exc)}, status_code=429)


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# Lifespan context manager for startup/shutdown
@app.on_event("startup")
async def startup_event():
    init_db()


@app.on_event("shutdown")
async def shutdown_event():
    pass

# Mount routers
app.include_router(auth_router, prefix='/api', tags=['Auth'])
app.include_router(performance_router, prefix='/api/performance', tags=['Performance'])
app.include_router(reliability_router, prefix='/api', tags=['Reliability'])
app.include_router(scalability_router, prefix='/api', tags=['Scalability'])
app.include_router(security_router, prefix='/api', tags=['Security'])
app.include_router(sessions_router, prefix='/api/documents', tags=['Sessions'])
app.include_router(usability_router, prefix='/api', tags=['Usability'])
app.include_router(users_router, prefix='/api/documents', tags=['Users'])

# AI_ROUTER_INJECTION_POINT — do not remove this line
# AI layer — mounted by Agent 8B
from ai.routes import router as ai_router
app.include_router(ai_router, prefix='/api/ai', tags=['AI'])

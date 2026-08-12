from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import auth, categories, expenses
from app.core.limiter import limiter

app = FastAPI(title="Expense API", version="0.1.0")
app.state.limiter = limiter

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "Validation failed", "details": exc.errors()})


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"error": f"Rate limit exceeded: {exc.detail}"})

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from . import models
from .routers import notes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event: create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown event
    pass

app = FastAPI(
    title="Notes API",
    description="A simple Notes API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    is_query_error = any(err.get("loc", [])[0] == "query" for err in errors)
    status_code = status.HTTP_400_BAD_REQUEST if is_query_error else status.HTTP_422_UNPROCESSABLE_ENTITY
    
    error_msgs = []
    for err in errors:
        loc = ".".join(map(str, err.get("loc", [])))
        msg = err.get("msg", "")
        error_msgs.append(f"{loc}: {msg}")
        
    message = "Validation Error: " + "; ".join(error_msgs)
    
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": status_code, "message": message}}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Notes API"}

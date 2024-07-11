from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from app.core.settings import settings
from app.setup_logging import setup_logging

load_dotenv()

from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi import FastAPI
from app.api.endpoints.v1 import router
from app.common.api_exceptions import RequestErrorHandler, RequestError
from app.middleware.request_middleware import RequestContextLogMiddleware


# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.executor = ProcessPoolExecutor()
    yield
    app.state.executor.shutdown()


# Create FastAPI app
app = FastAPI(**settings.app_config, lifespan=lifespan)

# Set up logging
logger = setup_logging()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    logger.error(f"Request Data Validation error: {exc}")
    for error in exc.errors():
        field = "->".join(error['loc'][1:])
        message = error['msg']
        errors.append({"field": field, "message": message})
    return JSONResponse(
        status_code=422,
        content={"detail": "Request Data Validation error", "errors": errors}
    )


app.include_router(router.api_router, prefix='/v1')
app.add_middleware(RequestContextLogMiddleware)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application.")


@app.exception_handler(RequestError)
async def request_error_internal(request, exc):
    reh = RequestErrorHandler(exc=exc)
    return reh.process_message()


@app.get("/", tags=["Base"])
async def root():
    return {"message": f"Welcome to the {settings.app_name} API"}

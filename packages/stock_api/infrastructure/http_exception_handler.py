from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from stock_api.application.exceptions import NotFoundException, BadRequestException


class HttpExceptionHandler:
    def __init__(self, app: FastAPI):
        self.app = app
        self._register_handlers()

    def _register_handlers(self):
        @self.app.exception_handler(NotFoundException)
        async def not_found(request: Request, exc: NotFoundException):
            return JSONResponse(status_code=404, content={"detail": str(exc)})

        @self.app.exception_handler(BadRequestException)
        async def bad_request(request: Request, exc: BadRequestException):
            return JSONResponse(status_code=400, content={"detail": str(exc)})

        @self.app.exception_handler(Exception)
        async def internal_error(request: Request, exc: Exception):
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )

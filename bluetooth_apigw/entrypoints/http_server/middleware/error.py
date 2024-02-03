import logging
from enum import auto
from typing import Callable

from aiohttp import web
from pydantic import BaseModel, Field
from bluetooth_apigw.common.auto_name import AutoName
from bluetooth_apigw.entrypoints.http_server.utils import json_response

logger = logging.getLogger(__name__)


class ErrorType(AutoName):
    server_error = auto()
    application_error = auto()
    unhandled_error = auto()
    client_error = auto()


class ErrorResponse(BaseModel):
    error_message: str
    error_type: ErrorType
    extra_info: dict = Field(default_factory=dict)


def error_middleware() -> Callable:
    @web.middleware
    async def middleware_handler(request: web.Request, handler: Callable) -> web.Response:
        try:
            return await handler(request)
        except web.HTTPException as ex:
            raise ex
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            return json_response(
                ErrorResponse(
                    error_message=str(ex),
                    error_type=ErrorType.unhandled_error,
                    extra_info={"error_class": str(ex.__class__)},
                ),
                status=500,
            )

    return middleware_handler

from aiohttp.web import Application, normalize_path_middleware
from aiohttp_pydantic import oas

from . import middleware, routes
from .config import BASE_DIR


def _get_middlewares():
    return (
        normalize_path_middleware(),
        middleware.error_middleware(),
    )


def create_app():
    app = Application(middlewares=_get_middlewares())

    api_app = Application(middlewares=_get_middlewares())
    api_app.add_routes(routes.service_router)
    api_app.add_routes(routes.ws_router)
    api_app.add_routes(routes.bluetooth_router)
    oas.setup(api_app, url_prefix="/docs")

    app.add_subapp("/api", api_app)

    return app

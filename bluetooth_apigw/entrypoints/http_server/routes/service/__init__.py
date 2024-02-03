from aiohttp import web

from .healthcheck import HealthcheckView

service_router = web.RouteTableDef()

service_router.view("/healthcheck")(HealthcheckView)

from aiohttp.web import RouteTableDef

from .notificatios import WSNotifications

ws_router = RouteTableDef()

ws_router.view("/notifications")(WSNotifications)

from aiohttp.web import RouteTableDef

from .characteristics import CharacteristicsView
from .connection import ConnectionView
from .connection_info import ConnectionInfoView
from .discover import DiscoverView

bluetooth_router = RouteTableDef()


bluetooth_router.view("/bluetooth/detect_devices")(DiscoverView)
bluetooth_router.view("/bluetooth/connect")(ConnectionView)
bluetooth_router.view("/bluetooth/connection_info")(ConnectionInfoView)
bluetooth_router.view("/bluetooth/characteristics")(CharacteristicsView)

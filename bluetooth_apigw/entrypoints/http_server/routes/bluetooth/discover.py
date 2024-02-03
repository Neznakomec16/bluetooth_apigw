from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200
from pydantic import BaseModel, Field
from bluetooth_apigw.entrypoints.http_server.utils import json_response
from bluetooth_apigw.bluetooth import gap
from asyncio import to_thread


async def discover_devices(scan_time: int):
    return await to_thread(gap.discover_devices, scan_time)


class DiscoveredDevice(BaseModel):
    bdaddr: str
    services_resolved: bool
    paired: bool
    connected: bool
    uuids: list[str] = Field(default_factory=list, alias='UUIDS')
    rssi: int | None = Field(None, alias='RSSI')
    ad_manufacturer_data_cid: int | None = None
    ad_manufacturer_data: str | None = None


class DiscoverDevicesResponse(BaseModel):
    devices: list[DiscoveredDevice]



class DiscoverView(PydanticView):
    
    async def get(self, scan_time: int = 2000) -> r200[DiscoverDevicesResponse]:
        """
        Tags: bluetooth
        """
        result = await discover_devices(scan_time)
        return json_response(DiscoverDevicesResponse(devices=result))

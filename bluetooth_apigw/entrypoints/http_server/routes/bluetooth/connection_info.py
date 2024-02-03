import asyncio

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200
from pydantic import BaseModel, Field
from bluetooth_apigw.bluetooth import gatt
from bluetooth_apigw.bluetooth.exceptions import StateError
from bluetooth_apigw.entrypoints.http_server.utils import json_response


class DiscoveredService(BaseModel):
    path: str
    uuid: str = Field(alias="UUID")


class DiscoveredServices(BaseModel):
    services: list[DiscoveredService]


async def discover_services(bdaddr: str) -> DiscoveredServices:
    results = await asyncio.to_thread(gatt.get_services, bdaddr)
    return DiscoveredServices(services=results)


class Descriptor(BaseModel):
    handle: str = Field(alias="path")
    uuid: str = Field(alias="UUID")
    characteristic_handle: str = Field(alias="characteristic_path")


class Characteristic(BaseModel):
    handle: str = Field(alias="path")
    uuid: str = Field(alias="UUID")
    service_handle: str = Field(alias="service_path")
    properties: list[str]
    descriptors: list[Descriptor]


class CharacteristicsItem(BaseModel):
    characteristics: list[Characteristic]
    handle: str = Field(alias="path")
    uuid: str = Field(alias="UUID")


class Characteristics(BaseModel):
    items: list[CharacteristicsItem]


def _get_characteristics(bdaddr: str, services: list[DiscoveredService]) -> Characteristics:
    results = []
    for service in services:
        result = gatt.get_characteristics(bdaddr, service.path)
        for characteristic in result:
            characteristic["descriptors"] = gatt.get_descriptors(bdaddr, characteristic["path"])
        results.append(
            {
                "path": service.path,
                "characteristics": result,
                "UUID": service.uuid,
            }
        )
    return Characteristics(items=results)


async def get_characteristics(bdaddr: str, services: DiscoveredServices) -> Characteristics:
    return await asyncio.to_thread(_get_characteristics, bdaddr, services.services)


class DiscoverServiceResponse(BaseModel):
    result: Characteristics | int


class ConnectionInfoView(PydanticView):

    async def get(self, bdaddr: str) -> r200[DiscoverServiceResponse]:
        """
        Tags: bluetooth
        """
        try:
            result = await discover_services(bdaddr)
        except StateError as e:
            return json_response(DiscoverServiceResponse(result=str(e)), status=400)
        characteristics = await get_characteristics(bdaddr, result)
        return json_response(characteristics)

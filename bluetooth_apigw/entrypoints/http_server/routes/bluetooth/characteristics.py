import asyncio

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200
from pydantic import BaseModel
from bluetooth_apigw.bluetooth.gatt import read_characteristic, write_characteristic
from bluetooth_apigw.bluetooth.utils import byteArrayToHexString
from bluetooth_apigw.entrypoints.http_server.utils import json_response


async def read_characteristics(bdaddr: str, handle: str):
    return await asyncio.to_thread(read_characteristic, bdaddr, handle)


async def write_characteristics(bdaddr: str, handle: str, value: str):
    return await asyncio.to_thread(write_characteristic, bdaddr, handle, value)


class CharacteristicsResponse(BaseModel):
    bdaddr: str
    handle: str
    result: int


class GetCharacteristicsResponse(CharacteristicsResponse):
    value: str


class WriteCharacteristicBody(BaseModel):
    bdaddr: str
    handle: str
    value: str


class WriteCharacteristicResponse(CharacteristicsResponse): ...


class CharacteristicsView(PydanticView):

    async def get(self, bdaddr: str, handle: str) -> r200[GetCharacteristicsResponse]:
        result = await read_characteristics(bdaddr, handle)
        return json_response(
            GetCharacteristicsResponse(
                bdaddr=bdaddr,
                handle=handle,
                value=byteArrayToHexString(result),
                result=0,
            )
        )

    async def put(self, body: WriteCharacteristicBody) -> r200[WriteCharacteristicResponse]:
        result = await write_characteristics(
            bdaddr=body.bdaddr,
            handle=body.handle,
            value=body.value,
        )
        return json_response(
            WriteCharacteristicResponse(
                bdaddr=body.bdaddr,
                handle=body.handle,
                result=result,
            )
        )

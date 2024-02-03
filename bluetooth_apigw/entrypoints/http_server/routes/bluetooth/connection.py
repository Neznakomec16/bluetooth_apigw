import asyncio

from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200
from pydantic import BaseModel
from bluetooth_apigw.bluetooth import gap
from bluetooth_apigw.entrypoints.http_server.utils import json_response


async def connect(bdaddr: str):
    return await asyncio.to_thread(gap.connect, bdaddr)


async def disconnect(bdaddr: str):
    return await asyncio.to_thread(gap.disconnect, bdaddr)


class ConnectionChangeResponse(BaseModel):
    status: int


class ConnectionView(PydanticView):

    async def put(self, bdaddr: str) -> r200[ConnectionChangeResponse]:
        """
        Tags: bluetooth
        """
        result = await connect(bdaddr)
        return json_response(ConnectionChangeResponse(status=result))

    async def delete(self, bdaddr: str) -> r200[ConnectionChangeResponse]:
        """
        Tags: bluetooth
        """
        result = await disconnect(bdaddr)
        return json_response(ConnectionChangeResponse(status=result))

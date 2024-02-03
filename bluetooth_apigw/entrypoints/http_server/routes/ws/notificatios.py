import asyncio
import enum
import json
import logging

import aiohttp
from aiohttp.web import WebSocketResponse
from aiohttp_pydantic import PydanticView
from pydantic import BaseModel
from bluetooth_apigw.bluetooth import gatt
from bluetooth_apigw.bluetooth.utils import byteArrayToHexString

logger = logging.getLogger(__name__)


class CommandType(enum.Enum):
    enable = 1
    disable = 0
    exit = 9


class Command(BaseModel):
    command: CommandType
    bdaddr: str
    handle: str


def handle_callback(ws: WebSocketResponse, bdaddr: str):
    def callback(handle: str, value: str):
        result = {
            "bdaddr": bdaddr,
            "handle": handle,
            "value": byteArrayToHexString(value),
            "result": 0,
        }
        if not ws.closed:
            asyncio.run(ws.send_json(result))

    return callback


async def handle_command(ws: WebSocketResponse, command: Command):
    match command.command:
        case CommandType.enable:
            await asyncio.to_thread(
                gatt.enable_notifications,
                command.bdaddr,
                command.handle,
                handle_callback(ws, command.bdaddr),
            )
        case CommandType.disable:
            await asyncio.to_thread(gatt.disable_notifications, command.bdaddr, command.handle)
        case CommandType.exit:
            await ws.close()
        case _:
            await ws.send_json({"error": "wrong command code"})


def _json_to_command(command_json: dict) -> Command:
    return Command(**command_json)


async def _handle_text(ws: WebSocketResponse, msg: str):
    try:
        command_json = json.loads(msg)
        command = _json_to_command(command_json)
    except json.JSONDecodeError:
        await ws.send_json({"error": "mailformed JSON"})
        return
    except ValueError as e:
        await ws.send_json({"error": str(e)})
        return
    await handle_command(ws, command)


class WSNotifications(PydanticView):

    async def get(self):
        ws = WebSocketResponse()
        await ws.prepare(self.request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await _handle_text(ws, msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info(f"ws connection closed with exception {ws.exception()}")
        return ws

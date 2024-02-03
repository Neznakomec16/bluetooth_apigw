import enum

from aiohttp.web import json_response
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.oas.typing import r200
from pydantic import BaseModel


class Status(enum.Enum):
    OK = "OK"


class HealthcheckResponse(BaseModel):
    status: Status


class HealthcheckView(PydanticView):
    async def get(self) -> r200[HealthcheckResponse]:
        """
        Tags: Service
        """

        return json_response({"status": Status.OK})

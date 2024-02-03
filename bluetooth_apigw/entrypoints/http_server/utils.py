import json
from typing import Any

from aiohttp.web import json_response as response
from pydantic import BaseModel


def json_response(
    data: dict[str, Any] | BaseModel | str | None,
    *,
    status: int = 200,
    reason: str | None = None,
    **kwargs,
):
    if isinstance(data, dict):
        text: str | None = json.dumps(data)
    elif isinstance(data, BaseModel):
        text = data.json()
    else:
        text = data
    return response(
        text=text,
        content_type="application/json",
        status=status,
        reason=reason,
        **kwargs,
    )

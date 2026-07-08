from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from piphi_runtime_kit_python import build_event_ingest_response
from piphi_runtime_kit_python.fastapi import sync_runtime_auth_from_fastapi_request

from ..contract import COMMANDS
from ..state import execute_command_for_entry, find_entry, runtime

router = APIRouter(tags=["commands"])


@router.post("/command")
async def command(payload: dict[str, Any], request: Request):
    sync_runtime_auth_from_fastapi_request(runtime, request)
    command_name = str(
        payload.get("command") or payload.get("capability_id") or ""
    ).strip()
    if not command_name:
        raise HTTPException(status_code=400, detail="Missing command")
    if command_name not in COMMANDS:
        raise HTTPException(
            status_code=400, detail=f"Unsupported command: {command_name}"
        )

    device_id = str(payload.get("device_id") or "").strip() or None
    config_id = str(payload.get("config_id") or "").strip() or None
    entry = find_entry(config_id=config_id, device_id=device_id)
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="No configured Tuya device matched the command target",
        )

    result = await execute_command_for_entry(
        entry, command_name, payload.get("args") or {}
    )
    event = {
        "event_type": "tuya.command.response",
        "device_id": entry["device_id"],
        "config_id": entry["config_id"],
        "payload": {
            "command": command_name,
            "state": result["state"],
        },
    }
    response = build_event_ingest_response(event)
    response_payload = (
        response.model_dump() if hasattr(response, "model_dump") else dict(response)
    )
    return {
        **response_payload,
        "ok": True,
        "command": command_name,
        "device_id": entry["device_id"],
        "state": result["state"],
        "result": result["result"],
    }

import logging

from fastapi import (
    APIRouter,
    Query,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)

from app.core.security import decode_access_token
from app.core.ws_manager import ws_manager

logger = logging.getLogger("websocket")
router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT Bearer Token"),
):
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        await websocket.close(code=1008)  # 1008 = Policy Violation / Unauthorized
        return

    user_id = int(payload["sub"])
    await ws_manager.connect(websocket, user_id=user_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text('{"event": "PONG"}')
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id=user_id)
    except (WebSocketException, RuntimeError, OSError) as e:
        logger.error(f"[WS] Error inesperado en socket usuario {user_id}: {e}")
        ws_manager.disconnect(websocket, user_id=user_id)

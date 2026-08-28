import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketException

logger = logging.getLogger("websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(
            f"[WS] Usuario {user_id} conectado. Conexiones activas: {len(self.active_connections[user_id])}"
        )

    def disconnect(self, websocket: WebSocket, user_id: int) -> None:
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"[WS] Usuario {user_id} desconectado.")

    async def broadcast_to_user(self, user_id: int, event_type: str, data: Any) -> None:
        """Emite un evento en tiempo real solo a los clientes del usuario correspondiente."""
        if user_id not in self.active_connections:
            return

        message = json.dumps({"event": event_type, "payload": data})
        for connection in list(self.active_connections[user_id]):
            try:
                await connection.send_text(message)
            except (WebSocketException, RuntimeError, OSError) as e:
                logger.error(f"[WS] Error al transmitir a usuario {user_id}: {e}")
                self.disconnect(connection, user_id)


ws_manager = ConnectionManager()

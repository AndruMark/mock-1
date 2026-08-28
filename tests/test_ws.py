import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.security import create_access_token
from app.models.user_model import User


def test_websocket_unauthorized(client: TestClient):
    with (
        pytest.raises(WebSocketDisconnect),
        client.websocket_connect("/ws?token=invalid-token"),
    ):
        pass


def test_websocket_authenticated_ping_pong(client: TestClient, test_user: User):
    token = create_access_token(data={"sub": str(test_user.id)})
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        websocket.send_text("ping")
        data = websocket.receive_text()
        assert "PONG" in data

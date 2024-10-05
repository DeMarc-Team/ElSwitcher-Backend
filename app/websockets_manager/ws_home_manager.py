from fastapi import WebSocket
from pydantic import BaseModel
from enum import Enum


class MessageType(Enum):
    ACTUALIZAR_PARTIDAS = "actualizar_partidas"


class WsMessage(BaseModel):
    action: MessageType
    data: str = None

    def json(self):
        # return {"action": self.action, "data": self.data}
        return self.model_dump_json()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        message = WsMessage(action=MessageType.ACTUALIZAR_PARTIDAS)
        await websocket.send_text(message.json())

    async def send_actualizar_partidas(self):
        await self.broadcast(WsMessage(action=MessageType.ACTUALIZAR_PARTIDAS))

    async def broadcast(self, message: WsMessage):
        for connection in self.active_connections.values():
            await connection.send_text(message.json())

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id)


ws_home_manager = ConnectionManager()

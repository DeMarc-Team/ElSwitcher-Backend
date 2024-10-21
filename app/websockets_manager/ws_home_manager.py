from fastapi import WebSocket
from pydantic import BaseModel
from enum import Enum
from uuid import uuid4

class MessageType(Enum):
    ACTUALIZAR_PARTIDAS = "actualizar_partidas"

ACTUALIZAR_PARTIDAS = MessageType.ACTUALIZAR_PARTIDAS.value

class WsMessage(BaseModel):
    action: MessageType
    data: str = None

    def json(self):
        return self.model_dump_json()

class HomeConnectionManager:
    """
    La clase del objeto con el cual se manejan las conexiones de websockets asociadas al Home.
    """

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        """
        Acepta la conexión del websocket recibido, le asigna un identificador
        aleatorio y lo almacena en un diccionario para poder accederlo.

        Retorna: user_id: int, el identificador generado para el usuario del home.
        """

        # Se setea un identificador interno para el websocket del usuario.
        user_id = uuid4()

        self.active_connections[user_id] = websocket

        # Aceptamos la conexion al final del todo, una vez que ya fue almacenada.
        await websocket.accept()

        return user_id

    async def send_actualizar_partidas(self):
        await self.broadcast(WsMessage(action=MessageType.ACTUALIZAR_PARTIDAS))

    async def broadcast(self, message: WsMessage):
        for connection in self.active_connections.values():
            await connection.send_text(message.json())

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id)


ws_home_manager = HomeConnectionManager()

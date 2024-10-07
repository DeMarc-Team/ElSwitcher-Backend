from fastapi import WebSocket
from pydantic import BaseModel
from enum import Enum


class MessageType(Enum):
    ACTUALIZAR_SALA_ESPERA = "actualizar_sala_espera"
    ACTUALIZAR_TURNO = "actualizar_turno"


class WsMessage(BaseModel):
    action: MessageType
    data: str = None

    def json(self):
        return self.model_dump_json()


class PartidasConnectionManager:
    def __init__(self):
        # Diccionario (id_partida, jugador_id) -> Websocket del jugador
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, partida_id: int, jugador_id: int, websocket: WebSocket):
        await websocket.accept()
        if partida_id not in self.active_connections.keys():
            self.active_connections[partida_id] = {}
        self.active_connections[partida_id][jugador_id] = websocket

    async def send_actualizar_sala_espera(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_SALA_ESPERA))
        
    async def send_actualizar_turno(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_TURNO))

    async def broadcast(self, partida_id: int, message: WsMessage):
        if partida_id in self.active_connections.keys():
            for connection in self.active_connections[partida_id].values():
                await connection.send_text(message.json())

    def disconnect(self, partida_id: int, jugador_id: int):
        self.active_connections[partida_id].pop(jugador_id)


ws_partidas_manager = PartidasConnectionManager()

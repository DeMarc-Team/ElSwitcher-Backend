from fastapi import WebSocket
from pydantic import BaseModel
from enum import Enum
from devtools.check_types import safe_type_check

class MessageType(Enum):
    ACTUALIZAR_SALA_ESPERA = "actualizar_sala_espera"
    ACTUALIZAR_TURNO = "actualizar_turno"
    ACTUALIZAR_TABLERO = "actualizar_tablero"
    ACTUALIZAR_CARTAS_MOVIMIENTO = "actualizar_cartas_movimiento"
    ACTUALIZAR_CARTAS_FIGURA = "actualizar_cartas_figura"
    HAY_GANADOR = "hay_ganador"
    PARTIDA_CANCELADA = "partida_cancelada"
    SINCRONIZAR_TURNO = "sincronizar_turno"
    SINCRONIZAR_MENSAJE = "sincronizar_mensaje"

ACTUALIZAR_SALA_ESPERA = MessageType.ACTUALIZAR_SALA_ESPERA.value
ACTUALIZAR_TURNO = MessageType.ACTUALIZAR_TURNO.value
HAY_GANADOR = MessageType.HAY_GANADOR.value
PARTIDA_CANCELADA = MessageType.PARTIDA_CANCELADA.value
ACTUALIZAR_TABLERO = MessageType.ACTUALIZAR_TABLERO.value
ACTUALIZAR_CARTAS_MOVIMIENTO = MessageType.ACTUALIZAR_CARTAS_MOVIMIENTO.value
ACTUALIZAR_CARTAS_FIGURA = MessageType.ACTUALIZAR_CARTAS_FIGURA.value
SINCRONIZAR_TURNO = MessageType.SINCRONIZAR_TURNO.value

class WsMessage(BaseModel):
    action: MessageType
    data: str = None

    def json(self):
        return self.model_dump_json()


class PartidasConnectionManager:
    """
    La clase del objeto con el cual se manejan las conexiones de websockets asociadas al interior de las partidas.
    """
    
    def __init__(self):
        # Diccionario (id_partida, jugador_id) -> Websocket del jugador
        self.active_connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, partida_id: int, jugador_id: int, websocket: WebSocket):
        """
        Acepta la conexión del websocket recibido y lo asocia con un jugador y una partida en un diccionario para poder accederlo.

        No retorna ningún valor.
        """
        
        await websocket.accept()
        if partida_id not in self.active_connections.keys():
            self.active_connections[partida_id] = {}
        self.active_connections[partida_id][jugador_id] = websocket

    @safe_type_check
    async def send_actualizar_sala_espera(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_SALA_ESPERA))

    @safe_type_check
    async def send_hay_ganador(self, partida_id: int, jugador_id: int, nombre: str):
        data = {
            "id": jugador_id,
            "nombre": nombre
        }
        mensaje = WsMessage(action=MessageType.HAY_GANADOR, data=str(data))

        await self.broadcast(partida_id, mensaje)

    @safe_type_check
    async def send_sincronizar_turno(self, partida_id: int, inicio: str, duracion: int):
        data = {
            "duracion": duracion,
            "inicio": inicio
        }
        mensaje = WsMessage(action=MessageType.SINCRONIZAR_TURNO, data=str(data))
        await self.broadcast(partida_id, mensaje)

    @safe_type_check
    async def send_actualizar_turno(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_TURNO))

    @safe_type_check
    async def send_actualizar_tablero(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_TABLERO))

    @safe_type_check
    async def send_actualizar_cartas_movimiento(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_CARTAS_MOVIMIENTO))

    @safe_type_check
    async def send_actualizar_cartas_figura(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.ACTUALIZAR_CARTAS_FIGURA))

    @safe_type_check
    async def send_partida_cancelada(self, partida_id: int):
        await self.broadcast(partida_id, WsMessage(action=MessageType.PARTIDA_CANCELADA))

    @safe_type_check
    async def send_sincronizar_mensaje(self, partida_id: int, jugador_id, mensaje):
        data = {
            "message": mensaje,
            "id_jugador": jugador_id,
            "type_message": "USER"
        }

        await self.broadcast(partida_id, WsMessage(action=MessageType.SINCRONIZAR_MENSAJE,data=str(data)))    

    async def broadcast(self, partida_id: int, message: WsMessage):
        if partida_id in self.active_connections.keys():
            for connection in self.active_connections[partida_id].values():
                await connection.send_text(message.json())

    def disconnect(self, partida_id: int, jugador_id: int):
        self.active_connections[partida_id].pop(jugador_id)
        if len(self.active_connections[partida_id]) == 0:
            self.active_connections.pop(partida_id)


ws_partidas_manager = PartidasConnectionManager()

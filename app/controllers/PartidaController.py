import crud.partidas as partida_service
import crud.jugadores as jugador_service
from websockets_manager.ws_home_manager import ws_home_manager
from websockets_manager.ws_partidas_manager import ws_partidas_manager

class PartidaController:
    def __init__(self, db):
        self.db = db

    async def get_partidas(self):
        return partida_service.get_partidas(self.db)

    async def get_partida_details(self, partida_id):
        response = partida_service.get_partida_details(self.db, partida_id)
        espacios_disponibles = 4 - len(response.jugadores)
        id_creador = partida_service.get_id_creador(self.db, partida_id)
        return {
            "id": response.id,
            "nombre_partida": response.nombre_partida,
            "nombre_creador": response.nombre_creador,
            "id_creador": id_creador,
            "iniciada": response.iniciada,
            "espacios_disponibles": espacios_disponibles
        }

    async def create_partida(self, partida):
        partida_details = partida_service.create_partida(self.db, partida)
        await ws_home_manager.send_actualizar_partidas()
        return partida_details

    async def iniciar_partida(self, partida_id):
        partida_service.iniciar_partida(self.db, partida_id)
        await ws_home_manager.send_actualizar_partidas()
        await ws_partidas_manager.send_actualizar_sala_espera(partida_id)
        return {"details": "Partida iniciada correctamente", "partida_id": partida_id}

    async def abandonar_partida(self, partida_id, jugador_id):
        eventos = partida_service.abandonar_partida(self.db, partida_id, jugador_id)
        hay_ganador = eventos.get("hay_ganador")
        partida_cancelada = eventos.get("partida_cancelada")
        if hay_ganador:
            await ws_partidas_manager.send_hay_ganador(partida_id, hay_ganador["id_ganador"], hay_ganador["nombre_ganador"])
        elif partida_cancelada:
            await ws_partidas_manager.send_partida_cancelada(partida_id)
            await ws_home_manager.send_actualizar_partidas()
        else:
            await ws_home_manager.send_actualizar_partidas()
            await ws_partidas_manager.send_actualizar_turno(partida_id)
            await ws_partidas_manager.send_actualizar_sala_espera(partida_id)
            await ws_partidas_manager.send_actualizar_tablero(partida_id)
        return {"detail": "El jugador abandonó la partida exitosamente"}

    async def get_jugadores(self, partida_id):
        return jugador_service.get_jugadores(self.db, partida_id)

    async def join_to_partida(self, partida_id: int, nombre_jugador: str):
        from models import Jugador # FIXME: Esto esta bien que se haga aca?
        jugador_on_create_response = jugador_service.create_jugador(self.db, Jugador(nombre=nombre_jugador, partida_id=partida_id))
        await ws_home_manager.send_actualizar_partidas()
        await ws_partidas_manager.send_actualizar_sala_espera(partida_id)
        return jugador_on_create_response
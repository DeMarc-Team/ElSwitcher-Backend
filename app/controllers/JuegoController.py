import crud.juego as juego_service
import crud.turno as turno_service
from websockets_manager.ws_partidas_manager import ws_partidas_manager
from figuras import hallar_todas_las_figuras_en_tablero
import json

from crud.TemporizadorTurno import temporizadores_turno

class JuegoController:
    def __init__(self, db):
        self.db = db

    async def get_cartas_figura_jugador(self, partida_id, jugador_id):
        return juego_service.get_cartas_figura_jugador(self.db, partida_id, jugador_id)

    async def get_movimientos_jugador(self, id_partida, id_jugador):
        return juego_service.get_movimientos_jugador(self.db, id_partida, id_jugador)

    async def get_turno_details(self, partida_id):
        return turno_service.get_turno_details(self.db, partida_id)

    async def terminar_turno(self, id_partida, id_jugador):
        turno_service.verificar_paso_de_turno(self.db, id_partida, id_jugador)
        await terminar_temporizador_del_turno(self.db, id_partida, id_jugador)

    async def get_tablero(self, id_partida):
        """Obtiene el tablero de una partida."""
        tablero = juego_service.get_tablero(self.db, id_partida)
        tablero_deserializado = json.loads(tablero)
        response = {
            'tablero': tablero_deserializado,
            'figuras_a_resaltar': hallar_todas_las_figuras_en_tablero(tablero_deserializado)
        }
        return response

    async def modificar_casillas(self, id_partida, id_jugador, coordenadas):
        juego_service.modificar_casillas(id_partida, id_jugador, coordenadas, self.db)
        await ws_partidas_manager.send_actualizar_tablero(id_partida)
        await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def deshacer_movimiento(self, id_partida):
        juego_service.deshacer_movimiento(self.db, id_partida)
        await ws_partidas_manager.send_actualizar_tablero(id_partida)
        await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def get_movimientos_parciales(self, id_partida):
        return juego_service.get_movimientos_parciales(self.db, id_partida)

    async def completar_figura_propia(self, id_partida, id_jugador, figura_data):
        eventos = juego_service.completar_figura_propia(self.db, id_partida, id_jugador, figura_data)
        hay_ganador = eventos.get("hay_ganador")
        if (hay_ganador):
            id_ganador = hay_ganador.get("id_ganador")
            nombre_ganador = hay_ganador.get("nombre_ganador")
            await ws_partidas_manager.send_hay_ganador(id_partida, id_ganador, nombre_ganador)
        else:
            await ws_partidas_manager.send_actualizar_cartas_figura(id_partida)
            await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)
            
    async def bloquear_carta_ajena(self, id_partida, id_jugador, bloqueo_data):
        juego_service.bloquear_carta_ajena(self.db, id_partida, id_jugador, bloqueo_data)
            
async def terminar_turno(db, id_partida, id_jugador):
    temporizadores_turno.cancelar_temporizador_del_turno(id_partida)
    turno_service.terminar_turno(db, id_partida)
    await ws_partidas_manager.send_actualizar_turno(id_partida)
    await ws_partidas_manager.send_actualizar_tablero(id_partida)
    await iniciar_temporizador_turno(db, id_partida)

async def iniciar_temporizador_turno(db, id_partida):
    id_jugador = turno_service.get_id_jugador_turno(db, id_partida)
    inicio, duracion = await temporizadores_turno.iniciar_temporizador_del_turno(id_partida, terminar_turno, (db, id_partida, id_jugador))
    await ws_partidas_manager.send_sincronizar_turno(id_partida, inicio, duracion)
    
async def terminar_temporizador_del_turno(db, id_partida, id_jugador):
    await temporizadores_turno.terminar_temporizador_del_turno(id_partida,terminar_turno,(db, id_partida, id_jugador))
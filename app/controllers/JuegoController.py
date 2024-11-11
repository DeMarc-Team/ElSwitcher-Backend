import service.juego as juego_service
import service.turno as turno_service
import service.partidas as partida_service
from websockets_manager.ws_partidas_manager import ws_partidas_manager
from websockets_manager.ws_home_manager import ws_home_manager
from service.figuras import hallar_todas_las_figuras_en_tablero
import json

from service.TemporizadorTurno import temporizadores_turno

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

        await log_action(id_partida, id_jugador, "Ha finalizado el turno del jugador")

        await terminar_temporizador_del_turno(self.db, id_partida)

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
        
        await log_action(id_partida, id_jugador, "Ha realizado un movimiento")

        await ws_partidas_manager.send_actualizar_tablero(id_partida)
        await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def deshacer_movimiento(self, id_partida, id_jugador):
        juego_service.deshacer_movimiento(self.db, id_partida)

        await log_action(id_partida, id_jugador, "Ha deshecho su último movimiento")

        await ws_partidas_manager.send_actualizar_tablero(id_partida)
        await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def get_movimientos_parciales(self, id_partida):
        return juego_service.get_movimientos_parciales(self.db, id_partida)

    async def completar_figura_propia(self, id_partida, id_jugador, figura_data):
        juego_service.verificar_color_prohibido(id_partida, figura_data.figura)
        juego_service.completar_figura_propia(self.db, id_partida, id_jugador, figura_data)

        if (ganador := juego_service.determinar_ganador_por_terminar_mazo(self.db, id_partida, id_jugador).get("ganador")):
            await ws_partidas_manager.send_hay_ganador(id_partida, ganador.get("id"), ganador.get("nombre"))
            partida_service.eliminar_partida(self.db, id_partida)
            await ws_home_manager.send_actualizar_partidas_activas(id_partida)
        else:
            await log_action(id_partida, id_jugador, "Ha completado una de sus cartas de figura")
            await ws_partidas_manager.send_actualizar_cartas_figura(id_partida)
            await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def bloquear_carta_ajena(self, id_partida, id_jugador, bloqueo_data):
        juego_service.verificar_color_prohibido(id_partida, bloqueo_data.figura)
        juego_service.bloquear_carta_ajena(self.db, id_partida, id_jugador, bloqueo_data)

        await log_action(id_partida, id_jugador, "Ha bloqueado la carta de otro jugador")

        await ws_partidas_manager.send_actualizar_cartas_figura(id_partida)
        await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida)

    async def get_cronometro(self, id_partida):
        turno_service.verificar_partida_iniciada(id_partida)
        inicio, duracion = turno_service.get_inicio_y_duracion_turno(id_partida)
        return { "inicio": inicio, "duracion": duracion }

    async def get_color_prohibido(self, id_partida):
        color = juego_service.get_color_prohibido(id_partida)
        return {"color": color}

    async def post_chat_message(self, id_partida, jugador_id, mensajeRequest):
        juego_service.verificar_partida_existe_y_jugador_pertenece(id_partida, jugador_id)
        nombre_jugador = juego_service.get_nombre_del_jugador(jugador_id)
        mensaje = nombre_jugador + ": " + mensajeRequest.message

        await ws_partidas_manager.send_sincronizar_mensaje(id_partida, jugador_id, mensaje)

        return {"detail": f"Mensaje enviado correctamente por {nombre_jugador}"}


async def terminar_turno(db, id_partida):
    temporizadores_turno.cancelar_temporizador_del_turno(id_partida)
    turno_service.terminar_turno(db, id_partida)
    await ws_partidas_manager.send_actualizar_turno(id_partida)
    await ws_partidas_manager.send_actualizar_tablero(id_partida)
    await iniciar_temporizador_turno(db, id_partida)

async def iniciar_temporizador_turno(db, id_partida):
    inicio, duracion = await temporizadores_turno.iniciar_temporizador_del_turno(id_partida, terminar_turno, (db, id_partida))
    await ws_partidas_manager.send_sincronizar_turno(id_partida, inicio, duracion)

async def terminar_temporizador_del_turno(db, id_partida):
    await temporizadores_turno.terminar_temporizador_del_turno(id_partida,terminar_turno,(db, id_partida))

def log_action(id_partida, id_jugador, mensaje):
    juego_service.verificar_partida_existe_y_jugador_pertenece(id_partida, id_jugador)
    nombre_jugador = juego_service.get_nombre_del_jugador(id_jugador)
    mensaje = nombre_jugador + ": " + mensaje
    return ws_partidas_manager.send_sincronizar_mensaje_log(id_partida, id_jugador, mensaje)

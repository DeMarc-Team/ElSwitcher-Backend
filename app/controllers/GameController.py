import crud
from figuras import hallar_todas_las_figuras_en_tablero
import json

class GameController:
    def __init__(self, db, communicator):
        self.db = db
        self.communicator = communicator

    async def get_cartas_figura_jugador(self, partida_id, jugador_id):
        return crud.partidas.get_cartas_figura_jugador(self.db, partida_id, jugador_id)

    async def get_movimientos_jugador(self, id_partida, id_jugador):
        return crud.juego.get_movimientos_jugador(self.db, id_partida, id_jugador)

    async def get_turno_details(self, partida_id):
        return crud.juego.get_turno_details(self.db, partida_id)

    async def terminar_turno(self, id_partida, id_jugador):
        crud.juego.terminar_turno(self.db, id_partida, id_jugador)
        await self.communicator.send_actualizar_turno(id_partida)
        await self.communicator.send_actualizar_tablero(id_partida)

    async def get_tablero(self, id_partida):
        """Obtiene el tablero de una partida."""
        tablero = crud.juego.get_tablero(self.db, id_partida)
        tablero_deserializado = json.loads(tablero)
        response = {
            'tablero': tablero_deserializado,
            'figuras_a_resaltar': hallar_todas_las_figuras_en_tablero(tablero_deserializado)
        }
        return response

    async def modificar_casillas(self, id_partida, id_jugador, coordenadas):
        crud.juego.modificar_casillas(id_partida, id_jugador, coordenadas, self.db)
        await self.communicator.send_actualizar_tablero(id_partida)
        await self.communicator.send_actualizar_cartas_movimiento(id_partida)

    async def deshacer_movimiento(self, id_partida):
        crud.juego.deshacer_movimiento(self.db, id_partida)
        await self.communicator.send_actualizar_tablero(id_partida)
        await self.communicator.send_actualizar_cartas_movimiento(id_partida)

    async def get_movimientos_parciales(self, id_partida):
        return crud.juego.get_movimientos_parciales(self.db, id_partida)

    async def completar_figura_propia(self, id_partida, id_jugador, figura_data):
        eventos = crud.juego.completar_figura_propia(self.db, id_partida, id_jugador, figura_data)
        hay_ganador = eventos.get("hay_ganador")
        if (hay_ganador):
            id_ganador = hay_ganador.get("id_ganador")
            nombre_ganador = hay_ganador.get("nombre_ganador")
            await self.communicator.send_hay_ganador(id_partida, id_ganador, nombre_ganador)
        else:
            await self.communicator.send_actualizar_cartas_figura(id_partida)
            await self.communicator.send_actualizar_cartas_movimiento(id_partida)
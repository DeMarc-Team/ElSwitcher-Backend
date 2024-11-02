import asyncio
import time
import warnings

from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO

class TemporizadorTurno:

    def __init__(self):
        self.temporizadores = {}
    
    async def __pasar_el_turno_por_temporizador(self, partida_id: int, func: callable, args: tuple):
        await func(*args)
        del self.temporizadores[partida_id]
        print(f"Se pasó el turno de la partida con ID {partida_id} por temporizador.")

    async def __iniciar_temporizador(self, partida_id: int, func: callable, args: tuple, duracion: int):
        await asyncio.sleep(duracion)
        await self.__pasar_el_turno_por_temporizador(partida_id, func, args)

    def iniciar_temporizador_del_turno(self, partida_id: int, func: callable, args: tuple, duracion: int = SEGUNDOS_TEMPORIZADOR_TURNO) -> tuple:
        """
        Inicia el temporizador del turno actual de una partida.
        Si ya existe el temporizador, lo cancela, elimina y reemplaza lanzando un warning.
        Al finalizar el temporizador, se pasará el turno al siguiente jugador.

        :PRE: La partida con ID partida_id existe y está iniciada.

        :param partida_id: ID de la partida.
        :param func: Función a ejecutar al finalizar el temporizador.
        :param args: Argumentos de la función.
        :param duracion: Duración del temporizador en segundos.

        :return: Tupla (tiempo de inicio, duración) del temporizador.
        """
        if partida_id in self.temporizadores:
            self.cancelar_temporizador_del_turno(partida_id)
            warnings.warn(f"El temporizador para la partida con ID {partida_id} ya estaba activo!, se lo cancelo y reemplazo.", Warning)

        loop = asyncio.get_event_loop()

        tarea = loop.create_task(self.__iniciar_temporizador(partida_id, func, args, duracion))
        self.temporizadores[partida_id] = tarea
        
        return time.gmtime(), duracion
     
    def cancelar_temporizador_del_turno(self, partida_id: int) -> None:
        """
        Cancela el temporizador del turno de una partida si existe.

        :param partida_id: ID de la partida.
        """
        if partida_id in self.temporizadores:
            self.temporizadores[partida_id].cancel()
            del self.temporizadores[partida_id]
            print(f"Temporizador para la partida con ID {partida_id} cancelado.")
        else:
            print(f"No hay temporizador para cancelar activo para la partida con ID {partida_id}.")

    def tiene_temporizador_del_turno(self, partida_id: int) -> bool:
        """
        Devuelve True si la partida tiene un temporizador del turno activo, False en caso contrario.

        :param partida_id: ID de la partida.

        :return: True si la partida tiene un temporizador del turno activo, False en caso contrario.
        """
        return partida_id in self.temporizadores
            
temporizadores_turno = TemporizadorTurno()

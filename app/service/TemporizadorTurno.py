import asyncio
import time
import warnings

from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO
from exceptions import ResourceNotFoundError, ForbiddenError
from DB.repository import PartidaRepo

# NOTE: Ningun warning deberia suceder en produccion.

class TemporizadorTurno:

    def __init__(self):
        self.temporizadores = {}
        self.lock = asyncio.Lock()

    async def __pasar_el_turno_por_temporizador(self, partida_id: int, terminar_turno: callable, args: tuple):
        try:
            del self.temporizadores[partida_id]
            await self.__ejecutar_funcion(terminar_turno, args)
        except ResourceNotFoundError as e:
            warnings.warn(
                f"ResourceNotFoundError al pasar el turno por temporizador de la partida con ID {partida_id}: {e}", Warning)
        except ForbiddenError as e:
            warnings.warn(
                f"ForbiddenError al pasar el turno por temporizador de la partida con ID {partida_id}: {e}", Warning)

    async def __iniciar_temporizador(self, partida_id: int, terminar_turno: callable, args: tuple, duracion: int):
        await asyncio.sleep(duracion)
        await self.__pasar_el_turno_por_temporizador(partida_id, terminar_turno, args)

    async def terminar_temporizador_del_turno(self, partida_id: int, terminar_turno: callable, args: tuple) -> None:
        """
        Termina el temporizador del turno de una partida y ejecuta la función asociada 
        al temporizador.

        Si no existe, lanza un warning y ejecuta la función con los argumentos pasados 
        por parametro.

        :param partida_id: ID de la partida.
        """
        async with self.lock:
            if partida_id in self.temporizadores:
                tarea = self.temporizadores[partida_id]
                if tarea.done():
                    warnings.warn(
                        f"Se intento terminar con una tarea registrada, pero ya habia terminado. ID: {partida_id}", Warning)
                    # FIXME: GRAVE? En los test sucede este warning. Anda todo igual (no se si es bueno)
                    # pero se podria arreglar. En produccion no se da este warning, si se da
                    # definitivamente puede ser grave.
                else:
                    terminar_turno = tarea.get_coro().cr_frame.f_locals['terminar_turno']
                    args = tarea.get_coro().cr_frame.f_locals['args']
                    self.cancelar_temporizador_del_turno(partida_id)
            else:
                warnings.warn(
                    f"Se intento terminar con una tarea, pero no estaba registrada. ID: {partida_id}", Warning)
                # FIXME: No es grave. En los test sucede este warning. Anda todo igual
                # pero se podria arreglar. En produccion no se da este warning pero si se da,
                # no es grave.
        await self.__ejecutar_funcion(terminar_turno, args)

    async def __ejecutar_funcion(self, func: callable, args: tuple) -> None:
        if asyncio.iscoroutinefunction(func):
            await func(*args)
        else:
            func(*args)

    async def iniciar_temporizador_del_turno(self, partida_id: int, terminar_turno: callable, args: tuple, duracion: int = SEGUNDOS_TEMPORIZADOR_TURNO) -> tuple:
        """
        Inicia el temporizador del turno actual de una partida.
        Si ya existe el temporizador, lo cancela, elimina y reemplaza lanzando un warning.
        Al finalizar el temporizador, se pasará el turno al siguiente jugador.

        :PRE: La partida con ID partida_id existe y está iniciada.

        :param partida_id: ID de la partida.
        :param terminar_turno: Función a ejecutar al finalizar el temporizador.
        :param args: Argumentos de la función.
        :param duracion: Duración del temporizador en segundos.

        :return: Tupla (tiempo de inicio en formato gmt zulu time, duración en segundos) del temporizador.
        """
        async with self.lock:
            if partida_id in self.temporizadores:
                self.cancelar_temporizador_del_turno(partida_id)
                warnings.warn(
                    f"Se intento iniciar una tarea, pero ya estaba registrada, se la cancelo y reemplazo. ID: {partida_id}", Warning)

            loop = asyncio.get_event_loop()

            tarea = loop.create_task(self.__iniciar_temporizador(
                partida_id, terminar_turno, args, duracion))
            self.temporizadores[partida_id] = tarea

            inicio_turno = self.get_gmt_zulu_time()
            duracion_turno = SEGUNDOS_TEMPORIZADOR_TURNO
            
            PartidaRepo().put_inicio_y_duracion_turno(partida_id, inicio_turno, duracion_turno)
            
            return inicio_turno, duracion_turno

    def get_gmt_zulu_time(self) -> str:
        """Devuelve el tiempo actual en formato GMT/UTC Zulu como un string en la forma 'YYYY-MM-DDTHH:MM:SSZ'."""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    def cancelar_temporizador_del_turno(self, partida_id: int) -> None:
        """
        Cancela el temporizador del turno de una partida si existe.

        :param partida_id: ID de la partida.
        """
        if partida_id in self.temporizadores:
            tarea = self.temporizadores[partida_id]
            del self.temporizadores[partida_id]
            tarea.cancel()

    def tiene_temporizador_del_turno(self, partida_id: int) -> bool:
        """
        Devuelve True si la partida tiene un temporizador del turno activo, False en caso contrario.

        :param partida_id: ID de la partida.

        :return: True si la partida tiene un temporizador del turno activo, False en caso contrario.
        """
        return partida_id in self.temporizadores


temporizadores_turno = TemporizadorTurno()

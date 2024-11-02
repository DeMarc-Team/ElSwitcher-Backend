from sqlalchemy.orm import Session
from crud.TemporizadorTurno import TemporizadorTurno
import asyncio
from models import (Partida,
                    Jugador,
                    CartaFigura,
                    CartaMovimiento,
                    MovimientoParcial
                    )
from constantes_juego import N_CARTAS_FIGURA_TOTALES

class TemporizadorTurnoToTest(TemporizadorTurno):
    def limpiar_temporizadores(self):
        """
        Cancela todos los temporizadores activos.
        """
        for partida_id, tarea in list(self.temporizadores.items()):
            tarea.cancel()
        self.temporizadores.clear()
        print("Todos los temporizadores han sido cancelados.")
        
    async def wait_for_all_tasks(self):
        """
        Espera a que todos los temporizadores activos y las tareas pendientes terminen.
        """
        async with self.lock:
            while self.temporizadores:
                await asyncio.sleep(1)
            tareas_pendientes = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.cancelled()]
            if tareas_pendientes:
                await asyncio.gather(*tareas_pendientes)

        
test_temporizadores_turno = TemporizadorTurnoToTest()

def crear_partida(db: Session, nombre_partida: str = "Partida", nombre_creador: str = "Creador") -> Partida:
    '''
    Función para crear una partida.

    Devuelve la partida creada y el jugador creador.

    Valores por defecto:
    - nombre_partida = Partida
    - nombre_creador = Creador
    - iniciada = False
    - tablero = '[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'
    '''
    partida = Partida(nombre_partida=nombre_partida,
                            nombre_creador=nombre_creador,
                            iniciada=False,
                            tablero='[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]')
    creador = Jugador(nombre=nombre_creador,
                      partidas=partida,
                      es_creador=True,
                      orden=0)
    partida.jugadores.append(creador)
    
    db.add(creador)
    db.add(partida)

    db.commit()
    return partida, creador


def unir_jugadores(db: Session, partida: Partida , numero_de_jugadores: int = 1) -> Jugador:
    '''
    Función para unir jugadores a una partida.

    Devuelve una lista con los jugadores unidos a la partida.
    Si numero_de_jugadores es 0, devuelve una lista vacía.

    Valores por defecto:
    - partida = Partida
    - numero_de_jugadores = 1
    - nombre = Jugador{i} donde i va desde 2 hasta 4
    '''
    assert partida.iniciada == False, "La partida ya ha sido iniciada"
    assert len(partida.jugadores) <= 4, "La partida ya tiene 4 jugadores"
    assert len(partida.jugadores) > 0, "Y el creador? boludito"
    assert numero_de_jugadores < 4, "No se pueden unir más de 4 jugadores a la partida"
    
    if numero_de_jugadores == 0:
        return []

    nuevos_jugadores = []
    for i in range(numero_de_jugadores):
        nuevo_jugador = Jugador(nombre=f"Jugador{i+2}", partidas=partida, es_creador=False, orden=len(partida.jugadores))
        db.add(nuevo_jugador)
        partida.jugadores.append(nuevo_jugador)
        nuevos_jugadores.append(nuevo_jugador)
        db.commit()

    db.commit()
    return nuevos_jugadores

def iniciar_partida(db: Session, partida: Partida) -> Partida:
    '''
    Función para iniciar una partida. (y reparte cartas de figura y movimiento)

    Devuelve la partida.

    Valores por defecto:
    - iniciada = True
    - repartir_cartas_figura = 3 cartas por jugador, 3 cartas reveladas
    - repartir_cartas_movimiento = 3 cartas por jugador
    '''
    assert partida.iniciada == False, "La partida ya ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder iniciarla"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    partida.iniciada = True

    numero_de_cartas_por_jugador = int(N_CARTAS_FIGURA_TOTALES/len(partida.jugadores))
    __repartir_cartas_figura(db, partida, 3, numero_de_cartas_por_jugador)
    __repartir_cartas_movimiento(db, partida, 3)

    db.commit()
    return partida

def __repartir_cartas_figura(db: Session, partida: Partida, n_cartas_reveladas, n_cartas_por_jugador):
    '''
    Función para repartir las cartas de figura a los jugadores de una partida.

    Valores por defecto:
    - n_cartas_por_jugador = 3
    '''
    assert n_cartas_por_jugador <= int(N_CARTAS_FIGURA_TOTALES/len(partida.jugadores))
    assert partida.iniciada == True, "La partida no ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder repartir las cartas de figura"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    # Crear las cartas de figura
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador - len(jugador.mazo_cartas_de_figura)):
            carta = CartaFigura(poseida_por=jugador, revelada=(i < n_cartas_reveladas))
            db.add(carta)
            jugador.mazo_cartas_de_figura.append(carta)

    db.commit()
    return partida


def __repartir_cartas_movimiento(db: Session, partida: Partida, n_cartas_por_jugador=3):
    '''
    Función para repartir las cartas de figura a los jugadores de una partida.

    Valores por defecto:
    - n_cartas_por_jugador = 3
    '''
    assert partida.iniciada == True, "La partida no ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder repartir las cartas de figura"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    # Crear las cartas de figura
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador - len(jugador.mano_movimientos)):
            carta = CartaMovimiento(movimientos_de=jugador)
            db.add(carta)
            jugador.mano_movimientos.append(carta)

def abandonar_partida(db: Session, partida: Partida, jugador: Jugador) -> Partida:
    '''
    Función para abandonar una partida.

    Devuelve la partida actualizada.
    '''
    assert not (not partida.iniciada and jugador.es_creador), "El creador no puede abandonar la partida antes de iniciarla"

    partida = db.query(Partida).filter(Partida.id == partida.id).first()
    
    partida.jugadores.remove(jugador)
    db.delete(jugador)
    db.flush()

    if (len(partida.jugadores) == 1):
        db.delete(partida)    

    db.commit()
    return partida

def siguiente_turno(db: Session, partida: Partida):
    '''
    Procedimiento para asignar el turno al siguiente jugador (en orden) de la partida.
    '''
    
    assert partida.iniciada == True, "La partida no ha sido iniciada"
    
    partida.jugadores.append(partida.jugadores.pop(0))
    db.flush()
    for jugador in partida.jugadores:
        jugador.orden = partida.jugadores.index(jugador)

    db.commit()

def consumir_carta_movimiento(db: Session, jugador: Jugador, mov: str, cantidad=1):
    '''
    Procedimiento para eliminar los primeros "cantidad" de movimientos de la mano del jugador que son del tipo "mov".
    
    En caso de existir menos movimientos de tipo "mov" de la cantidad a consumir especificada, se consumen todas las movimientos del tipo "mov" que hay.
    '''
    
    assert cantidad >= 1, "La cantidad de movimientos a consumir debe ser mayor o igual que 1."
    assert jugador.mano_movimientos is not None, "El jugador no tiene una mano de movimientos asignada (su mano es None)."
    assert jugador.mano_movimientos != [], "El jugador no tiene cartas de movimiento en su mano (su mano está vacía)."
    
    cartas_del_tipo = [carta for carta in jugador.mano_movimientos if carta.movimiento == mov]
    
    assert cartas_del_tipo is not None, f"El jugador no posee ninguna carta revelada del tipo '{mov}'."
    
    cartas_a_borrar = cartas_del_tipo[:cantidad]
    
    for carta in cartas_a_borrar:
        db.delete(carta)    
    
    db.commit()

def consumir_cantidad_cartas_figura_reveladas(db: Session, jugador: Jugador, cantidad:int = 1):
    '''
    Procedimiento para eliminar las primeras "cantidad" de cartas de figura reveladas de la mano del jugador.
    '''
    assert jugador.mazo_cartas_de_figura is not None, "El jugador no tiene una mano de cartas de figura asignada (su mano es None)."
    cartas_reveladas = [carta for carta in jugador.mazo_cartas_de_figura if carta.revelada]
    assert cartas_reveladas is not None, "El jugador no posee ninguna carta revelada."
    for carta in cartas_reveladas[:cantidad]:
        db.delete(carta)
    db.commit()

def consumir_cantidad_cartas_movimiento(db: Session, jugador: Jugador, cantidad:int=1):
    '''
    Procedimiento para eliminar las primeras "cantidad" de cartas de movimiento de la mano del jugador.
    '''
    assert jugador.mano_movimientos is not None, "El jugador no tiene una mano de movimientos asignada (su mano es None)."
    cartas = jugador.mano_movimientos
    assert cartas is not None, "El jugador no posee ninguna carta de movimiento."
    for carta in cartas[:cantidad]:
        db.delete(carta)
    db.commit()
 
def establecer_tablero(db: Session, partida: Partida, tablero: list[list[int]]):
    import json
    partida.tablero = json.dumps(tablero)
    
    db.commit()
    
def cartear_figuras(db: Session, jugador: Jugador, figs: list[str]):
    assert len(figs) > 0, "Se requiere al menos una carta."
    assert len(figs) <= 3, "Se puede cartar una única mano de figuras (3 cartas)."
    
    figuras_reveladas = [figura for figura in jugador.mazo_cartas_de_figura if figura.revelada]
    
    for figura in figuras_reveladas:
        db.delete(figura)
        db.commit()
    
    nuevas_figuras = [CartaFigura(figura=fig) for fig in figs]
    
    jugador.mazo_cartas_de_figura.extend(nuevas_figuras)
    
    db.commit()
    
def eliminar_cartas_figura_del_maso(db: Session, jugador: Jugador, numero_a_dejar: int):
    '''
    Elimina las cartas de figura del jugador dejando `numero_a_dejar` cartas.
    Elimina al ultimo las cartas reveladas si hay.
    '''
    figuras_no_reveladas = [figura for figura in jugador.mazo_cartas_de_figura if not figura.revelada]
    figuras_reveladas = [figura for figura in jugador.mazo_cartas_de_figura if figura.revelada]
    # Dejamos las figuras reveladas al final:
    figuras = figuras_no_reveladas + figuras_reveladas

    for i in range(len(figuras) - numero_a_dejar):
        db.delete(figuras[i])
        db.commit()
    

def listas_to_casillas_figura(figuras: list[list[(int, int)]]):
    '''
    Convierte una lista de casillas en formato de tuplas a una en formato de Casillas (como objeto).
    
    Por ejemplo:
    [ [(row_value1, col_value1)], [(row_value2, col_value2)] ] -> [ [{row: row_value1, col: col_value1}], [{row: row_value2, col: col_value2}] ]
    '''
    casillas_de_figuras = []
    
    for figura in figuras:
        casillas_figura = [{"row": tupla[0], "col": tupla[1]} for tupla in figura]
        casillas_de_figuras.append(casillas_figura)
        
    return casillas_de_figuras

def falsear_movimientos_parciales(db: Session, partida: Partida, movimientos: list[CartaMovimiento]):
    '''
    Crea movimientos parciales falsos a partir de la lista de cartas de movimiento pasadas.
    NOTA: Se presupone que las cartas están en la mano de un mismo jugador, aunque puede que ande de todas formas.
    '''
    
    assert len(movimientos) > 0, "Se esperaba al menos una carta."
    assert len(movimientos) <= 3, "Solo se pueden recibir a lo sumo 3 cartas."
    

    for carta in movimientos:
        orden = len(partida.movimientos_parciales)
        movimiento_parcial = MovimientoParcial(
            carta_id=carta.id,
            origen=str((0,0)),
            destino=str((1,1)),
            carta=carta,
            partida_id=partida.id,
            orden=orden
        )
        partida.movimientos_parciales.append(movimiento_parcial)
        db.commit()

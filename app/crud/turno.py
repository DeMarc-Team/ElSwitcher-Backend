from sqlalchemy.orm import Session
from crud.juego import deshacer_movimiento
import warnings # NOTE: Los warnings se usan para cosas que no deberian pasar, errores no esperados.

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador, CartaMovimiento
from schemas import TurnoDetails
from constantes_juego import N_FIGURAS_REVELADAS
from crud.repository import partida_repo

def get_inicio_y_duracion_turno(partida_id):
    """
    Devuelve inicio y duracion del cronometro de la partida.
    """
    return partida_repo.get_inicio_y_duracion_turno(partida_id)

def verificar_partida_iniciada(partida_id):
    """
    Lanza las excepciones correspondientes si la partida no esta iniciada.
    """
    partida_iniciada = partida_repo.get_iniciada(partida_id)
    if (not partida_iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} no esta iniciada.")

def get_turno_details(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {partida_id} todavía no comenzó.")

    nombre_jugador_del_turno = partida.jugador_del_turno.nombre

    turno_details = TurnoDetails(
        id_jugador=partida.jugador_id,
        nombre_jugador=nombre_jugador_del_turno
    )

    return turno_details

def verificar_paso_de_turno(db: Session, partida_id, jugador_id):
    """
    Lanza las excepciones correspondientes si el jugador no puede pasar el turno.
    """
    partida = db.get(Partida, partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    if (not partida.iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} todavía no comenzó.")
    if (partida.jugador_del_turno.id != jugador_id):
        raise ForbiddenError(f"El ID del jugador que posee el turno no es {jugador_id}.")


def get_id_jugador_turno(db: Session, partida_id):
    """
    Devuelve el ID del jugador que tiene el turno en la partida.
    """
    partida = db.get(Partida, partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    return partida.jugador_id

def terminar_turno(db: Session, partida_id):
    """
    Pasa el turno de la partida.
    
    :PRE: La partida debe estar iniciada y se puede pasar turno.
    """
    partida = db.get(Partida, partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    if (not partida.iniciada):
        warnings.warn(f"Se intento pasar el turno de la partida {partida_id} y no estaba iniciada.")
        raise ForbiddenError(f"La partida con ID {partida.id} todavía no comenzó.")

    
    __limpiar_stack_movimientos_parciales(db, partida, atomic=False)
    __reponer_cartas_movimiento(db, partida, partida.jugador_del_turno, atomic=False)
    
    if(not partida.jugador_del_turno.bloqueado):
        __reponer_cartas_figura(db, partida, partida.jugador_del_turno, atomic=False)
    elif ( len(partida.jugador_del_turno.mano_figuras) == 1 ):
        partida.jugador_del_turno.mano_figuras[0].bloqueada = False
    elif ( len(partida.jugador_del_turno.mano_figuras) == 0 ):
        partida.jugador_del_turno.bloqueado = False
        __reponer_cartas_figura(db, partida, partida.jugador_del_turno, atomic=False)
    
    db.flush()
    __siguiente_turno(db, partida, atomic=False)

    db.commit()

def __limpiar_stack_movimientos_parciales(db, partida, atomic=True):
    while partida.movimientos_parciales:
        deshacer_movimiento(db, partida.id, atomic=False) # FIXME: No llama a traves de controller
    
    if atomic:
        db.commit()
    else:
        db.flush()

def __reponer_cartas_movimiento(db: Session, partida: Partida, jugador: Jugador, n_cartas_por_jugador=3, atomic=True):
    '''
    Procedimiento para reponer las cartas movimiento de un jugador.
    
    Repone hasta que el jugador tenga n_cartas_por_jugador en la mano.
    '''
    
    cantidad_movimientos = len(jugador.mano_movimientos)

    # Reponemos las cartas de movimiento del jugador
    for i in range(0, n_cartas_por_jugador - cantidad_movimientos):
        new_carta = CartaMovimiento(jugador_id=jugador.id_jugador)
        db.add(new_carta)
        
    if atomic:
        db.commit()
    else:
        db.flush()

def __reponer_cartas_figura(db: Session, partida: Partida, jugador: Jugador, n_reveladas=N_FIGURAS_REVELADAS, atomic=True):
    '''
    Procedimiento para reponer las cartas figura de un jugador.
    
    Repone hasta que el jugador tenga n_reveladas en la mano.
    '''
    
    cartas_no_reveladas = [carta for carta in jugador.mazo_cartas_de_figura if not carta.revelada]
    cantidad_reveladas = len([carta for carta in jugador.mazo_cartas_de_figura if carta.revelada])
    cartas_a_revelar = min(len(cartas_no_reveladas), n_reveladas - cantidad_reveladas)

    for i in range(cartas_a_revelar):
        cartas_no_reveladas[i].revelada = True
    
    if atomic:
        db.commit()
    else:
        db.flush()

def __siguiente_turno(db: Session, partida, atomic=True):
    partida.jugadores.append(partida.jugadores.pop(0))
    db.flush()
    for jugador in partida.jugadores:
        jugador.orden = partida.jugadores.index(jugador)

    if atomic:
        db.commit()
    else:
        db.flush()
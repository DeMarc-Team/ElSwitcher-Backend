from sqlalchemy.orm import Session
from sqlalchemy import func
from random import shuffle

from exceptions import ResourceNotFoundError, ForbiddenError
from schemas import PartidaData
from models import Jugador, CartaFigura, CartaMovimiento, Partida
from constantes_juego import N_CARTAS_FIGURA_TOTALES, N_FIGURAS_REVELADAS
from crud.TemporizadorTurno import temporizadores_turno
from crud.repository import PartidaRepo

def get_id_creador(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    return partida.id_creador

def get_partidas(db: Session):
    subquery = (
        db.query(Partida.id, func.count(Partida.jugadores).label('jugadores_count'))
        .outerjoin(Partida.jugadores)
        .group_by(Partida.id)
    ).subquery()

    return db.query(Partida).join(subquery, Partida.id == subquery.c.id).filter(
        Partida.iniciada == False,
        subquery.c.jugadores_count < 4
    ).all()

def get_partida_details(db: Session, id: int):
    partidaDetails = db.query(Partida).filter(Partida.id == id).first()
    if (not partidaDetails):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
    return partidaDetails

def create_partida(db: Session, partida: PartidaData):
    
    desambiguar_eleccion_de_privacidad(partida)
    
    new_partida = Partida(nombre_partida=partida.nombre_partida, nombre_creador=partida.nombre_creador, privada=partida.privada, contraseña=partida.contraseña)
    db.add(new_partida)
    db.flush()
    new_jugador = Jugador(nombre=partida.nombre_creador, es_creador=True, partida_id=new_partida.id)
    db.add(new_jugador)
    db.commit()
    return new_partida

def desambiguar_eleccion_de_privacidad(partida: PartidaData):
    if (partida.privada == False or partida.contraseña == None or partida.contraseña == ""):
        partida.contraseña = ""
        partida.privada = False


def iniciar_partida(db: Session, id: int):
    partida = db.query(Partida).filter(Partida.id == id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
    
    if (partida.iniciada):
        raise ForbiddenError(f"La partida con ID {id} ya está iniciada.")
    
    if (not len(partida.jugadores) > 1):
        raise ForbiddenError(f"Partida con ID {id} no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.")

    partida.iniciada = True
    n_cartas_fig_por_jugador = int(N_CARTAS_FIGURA_TOTALES/len(partida.jugadores))
    _repartir_cartas_figura(db, partida, n_cartas_fig_por_jugador, N_FIGURAS_REVELADAS)
    _repartir_cartas_movimiento(db, partida)
    db.flush()
    shuffle(partida.jugadores)
    for jugador in partida.jugadores: # FIXME: Revisar si es necesario
        jugador.orden = partida.jugadores.index(jugador)
    db.commit()

def _repartir_cartas_figura(db: Session, partida, n_cartas_por_jugador=22, n_cartas_reveladas=N_FIGURAS_REVELADAS):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador-n_cartas_reveladas):
            new_carta = CartaFigura(jugador_id=jugador.id_jugador, revelada=False)
            db.add(new_carta)

        for i in range(n_cartas_reveladas):
            new_carta = CartaFigura(jugador_id=jugador.id_jugador, revelada=True)
            db.add(new_carta)
    
def _repartir_cartas_movimiento(db: Session, partida, n_cartas_por_jugador=3):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador):
            new_carta = CartaMovimiento(jugador_id=jugador.id_jugador)
            db.add(new_carta)

def abandonar_partida(db: Session, partida_id: int, jugador_id: int)->bool:
    '''
    Elimina al jugador de la partida. Si el creador abandona la partida antes de iniciarla, 
    elimina la partida (se cancela).
    
    :return: True si la partida fue cancelada, False en caso contrario.
    '''
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    id_creador = partida.id_creador
    
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    partida.jugadores.remove(jugador)
    db.delete(jugador)
    db.commit()

    return __partida_cancelada(db, partida, jugador, id_creador)

def es_su_turno(db: Session, partida_id: int, jugador_id: int)->bool:
    """
    Devuelve True si es el turno del jugador en la partida, False en caso contrario.
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    return partida.iniciada and jugador.id == partida.jugador_del_turno.id

def __partida_cancelada(db: Session, partida: Partida, jugador: Jugador, id_creador: int):
    if (not partida.iniciada and jugador.id_jugador == id_creador):
        eliminar_partida(db, partida)
        db.commit()
        return True
    return False

def hay_ganador(db: Session, partida_id: int):
    '''
    En la partida pasada por parametro, verifica si hay un ganador y lo
    devuelve.

    Un jugador gana si cumple alguna de las siguientes condiciones en orden
    de prioridad:

    1. Se queda en su turno sin cartas de figura en su maso.
    2. Es el único jugador en la partida.

    Retorna un diccionario con la siguiente estructura:
    - Si hay un ganador:
        {"hay_ganador" : {"id_ganador" : id_ganador, "nombre_ganador" : nombre_ganador}}
    - Si no hay un ganador:
        {"hay_ganador" : None}
    '''
    partida = db.get(Partida, partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    id_ganador = None
    nombre_ganador = None
    db.refresh(partida)
    if (partida.iniciada):
        if (partida.jugador_del_turno.numero_de_cartas_figura == 0):
            id_ganador = partida.jugador_del_turno.id_jugador
            nombre_ganador = partida.jugador_del_turno.nombre
        elif (len(partida.jugadores) == 1):
            id_ganador = partida.jugadores[0].id_jugador
            nombre_ganador = partida.jugadores[0].nombre
    
    # Aca pueden ir mas verificaciones para determinar si hay un ganador

    if (id_ganador is not None):
        eliminar_partida(db, partida)
        db.commit()
        return {"hay_ganador" : {"id_ganador" : id_ganador, "nombre_ganador" : nombre_ganador}}

    return {"hay_ganador" : None}


def eliminar_partida(db: Session, partida: Partida):
    temporizadores_turno.cancelar_temporizador_del_turno(partida.id)
    db.delete(partida)
    db.commit()
    

def validar_contraseña(contraseña,partida_id):
    partida = PartidaRepo.get_by_id(partida_id)
    if (partida.privada and partida.contraseña != contraseña):
        raise ForbiddenError("La contraseña provista es incorrecta")
    
    return
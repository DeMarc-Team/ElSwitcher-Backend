from sqlalchemy.orm import Session
from sqlalchemy import func
from random import shuffle

from exceptions import ResourceNotFoundError, ForbiddenError
from schemas import PartidaData
from models import Jugador, CartaFigura, CartaMovimiento, Partida

def get_id_creador(db: Session, partida_id):
    jugador = db.query(Jugador).filter((Jugador.es_creador == True) & (Jugador.partida_id == partida_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    return jugador.id_jugador

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
    new_partida = Partida(nombre_partida=partida.nombre_partida, nombre_creador=partida.nombre_creador)
    db.add(new_partida)
    db.flush()
    new_jugador = Jugador(nombre=partida.nombre_creador, es_creador=True, partida_id=new_partida.id)
    db.add(new_jugador)
    db.commit()
    return new_partida

def iniciar_partida(db: Session, id: int):
    partida = db.query(Partida).filter(Partida.id == id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
    
    if (partida.iniciada):
        raise ForbiddenError(f"La partida con ID {id} ya está iniciada.")
    
    if (not len(partida.jugadores) > 1):
        raise ForbiddenError(f"Partida con ID {id} no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.")

    partida.iniciada = True
    _repartir_cartas_figura(db, partida,3,3)
    _repartir_cartas_movimiento(db, partida)
    db.flush()
    shuffle(partida.jugadores)
    db.commit()

def get_cartas_figura_jugador(db: Session, partida_id, jugador_id):
    
    partida = get_partida_details(db, partida_id) # raises ResourceNotFoundError if not found
    
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    mazo_del_jugador = jugador.mazo_cartas_de_figura

    return mazo_del_jugador

def _repartir_cartas_figura(db: Session, partida, n_cartas_por_jugador=3, n_cartas_reveladas=2):
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

def abandonar_partida(db: Session, partida_id: int, jugador_id: int):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")

    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    if (jugador.id_jugador == partida.id_creador and not partida.iniciada):
        raise ForbiddenError(f"El creador con ID {jugador_id} no puede abandonar la partida con ID {partida_id} antes de iniciarla.")
    
    partida.jugadores.remove(jugador)
    db.delete(jugador)
    db.flush()

    if (len(partida.jugadores) <= 1 and partida.iniciada):
        # TODO: Declarar ganador al jugador que queda
        db.delete(partida)    
    
    db.commit()
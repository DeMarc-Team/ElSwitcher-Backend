from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from crud.exceptions import PartidaNotFoundError, PartidaLlenaError
from models.jugadores import Jugador
from schemas.jugadores import JugadorData
from crud.partidas import get_partida_by_id

def create_jugador(db: Session, jugador: JugadorData):
    
    partida = get_partida_by_id(db, jugador.partida_id)
    if (not partida):
        raise PartidaNotFoundError(jugador.partida_id)
    
    numero_jugadores = db.query(Jugador).filter(Jugador.partida_id == jugador.partida_id).count()
    if (numero_jugadores >= 4):
        raise PartidaLlenaError(jugador.partida_id, 4)
    
    try:
        new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id)
        db.add(new_jugador)
        db.commit()
        db.flush()
        return new_jugador
    except Exception as e:
        db.rollback()
        raise e

def get_jugadores(db: Session, partida_id: int):
    if (get_partida_by_id(db, partida_id)):
        jugadores = db.query(Jugador).filter(Jugador.partida_id == partida_id).all()
    else:
        raise PartidaNotFoundError(partida_id)
    return jugadores
    
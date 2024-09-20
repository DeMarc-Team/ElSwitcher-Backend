from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .exceptions import PartidaNotFoundError
from models.jugadores import Jugador
from schemas.jugadores import JugadorData


def create_jugador(db: Session, jugador: JugadorData):
    new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id)
    try:
        new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id)
        db.add(new_jugador)
        db.commit()
        db.flush()
        return new_jugador
    except IntegrityError:
        db.rollback()
        raise PartidaNotFoundError(jugador.partida_id)

def get_jugadores(db: Session, partida_id: int):
    jugadores = db.query(Jugador).filter(Jugador.partida_id == partida_id).all()
    return jugadores
    
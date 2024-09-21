from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.crud.exceptions import PartidaNotFoundError
from app.models.jugadores import Jugador
from app.schemas.jugadores import JugadorData
from app.crud.partidas import get_partida_by_id

def create_jugador(db: Session, jugador: JugadorData):
    new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id)
    if (get_partida_by_id(db, jugador.partida_id)):
        new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id)
        db.add(new_jugador)
        db.commit()
        db.flush()
        return new_jugador
    else:
        raise PartidaNotFoundError(jugador.partida_id)

def get_jugadores(db: Session, partida_id: int):
    if (get_partida_by_id(db, partida_id)):
        jugadores = db.query(Jugador).filter(Jugador.partida_id == partida_id).all()
    else:
        raise PartidaNotFoundError(partida_id)
    return jugadores
    
from sqlalchemy.orm import Session

from crud.exceptions import PartidaYaIniciada, PartidaNotFoundError, PartidaLlenaError
from models import Jugador
from schemas import JugadorData
from crud.partidas import get_partida_details

def create_jugador(db: Session, jugador: JugadorData):
    
    partida = get_partida_details(db, jugador.partida_id)
    if (not partida):
        raise PartidaNotFoundError(jugador.partida_id)
    
    if (partida.iniciada):
        raise PartidaYaIniciada(jugador.partida_id)
    
    numero_jugadores = len(partida.jugadores)
    if (numero_jugadores >= 4):
        raise PartidaLlenaError(jugador.partida_id, 4)
    
    try:
        new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id, mazo_cartas_de_figura=[])
        db.add(new_jugador)
        db.commit()
        db.flush()
        return new_jugador
    except Exception as e:
        db.rollback()
        raise e

def get_jugadores(db: Session, partida_id: int):
    partida = get_partida_details(db, partida_id)
    if (not partida):
        raise PartidaNotFoundError(partida_id)

    return db.query(Jugador).filter(Jugador.partida_id == partida_id).all()

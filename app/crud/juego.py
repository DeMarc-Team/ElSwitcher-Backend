from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador
from schemas import TurnoDetails

def siguiente_turno(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    if (not partida.iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} todavía no comenzó.")
    
    juego = partida.juego[0]
    actual_jugador = juego.jugadores[0]
    juego.jugadores.remove(actual_jugador)
    db.flush()
    actual_jugador.orden = len(juego.jugadores)
    juego.jugadores.append(actual_jugador)
    db.commit()
    
    return actual_jugador.id_jugador

def terminar_turno(db: Session, partida_id, jugador_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    if (not partida.iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} todavía no comenzó.")
    
    juego = partida.juego[0]
    actual_jugador = juego.jugadores[0]
    
    if (actual_jugador.id_jugador != jugador_id):
        raise ForbiddenError(f"El ID del jugador que posee el turno no es {jugador_id}.")
    
    siguiente_turno(db, partida_id)


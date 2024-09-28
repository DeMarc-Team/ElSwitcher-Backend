from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador
from schemas import TurnoDetails

def get_movimientos_jugador(db: Session, partida_id: int, jugador_id: int):
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    movimientos_del_jugador = jugador.mano_movimientos
    return movimientos_del_jugador

def get_turno_details(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    if (not partida.iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} todavía no comenzó.")
    
    juego = partida.juego[0]
    
    nombre_jugador_del_turno = juego.jugador_del_turno.nombre
    
    turno_details = TurnoDetails(
        id_jugador=juego.jugador_id,
        nombre_jugador=nombre_jugador_del_turno
    )
    
    return turno_details
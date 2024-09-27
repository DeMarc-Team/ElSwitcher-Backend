from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError
from models import Partida, Jugador, TurnoDetails

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
    
    try:
        juego = partida.juego[0]
    except:
        raise ResourceNotFoundError(f"Juego asociado a la partida con ID {partida_id} no encontrado.")
    
    nombre_jugador_del_turno = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == juego.turno)).first().nombre
    
    turno_details = TurnoDetails(
        id_jugador=juego.turno,
        nombre_jugador=nombre_jugador_del_turno
    )
    
    return turno_details
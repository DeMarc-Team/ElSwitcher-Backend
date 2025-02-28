from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from db.models import Jugador
from schemas import JugadorData
from services.partidas import get_partida_details

def create_jugador(db: Session, jugador: JugadorData):
    
    partida = get_partida_details(db, jugador.partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {jugador.partida_id} no encontrada.")
    
    if (partida.iniciada):
        raise ForbiddenError(f"La partida con ID {jugador.partida_id} ya está iniciada.")
    
    numero_jugadores = len(partida.jugadores)
    if (numero_jugadores >= 4):
        raise ForbiddenError(f"Partida con ID {jugador.partida_id} está llena. Máximo de jugadores: 4.")
    
    try:
        # WARNING: La asignación del orden actualmente podría generar race conditions
        new_jugador = Jugador(nombre=jugador.nombre, partida_id=jugador.partida_id, orden=len(partida.jugadores), mazo_cartas_de_figura=[])
        db.add(new_jugador)
        db.commit()
        return new_jugador
    except Exception as e:
        db.rollback()
        raise e

def get_jugadores(db: Session, partida_id: int):
    partida = get_partida_details(db, partida_id)
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")

    return db.query(Jugador).filter(Jugador.partida_id == partida_id).all()


def set_movement_card_used(db: Session, jugador:Jugador, mov_id):
    for movimiento in jugador.mano_movimientos:
        if (movimiento.movimiento == mov_id and movimiento.usada_en_movimiento_parcial == False):
            movimiento.usada_en_movimiento_parcial = True

            db.commit()
            return
        
def set_movement_card_unused(db: Session, jugador:Jugador, mov_id):
    for movimiento in jugador.mano_movimientos:
        if (movimiento.movimiento == mov_id and movimiento.usada_en_movimiento_parcial == True):
            movimiento.usada_en_movimiento_parcial = False

            db.commit()
            return
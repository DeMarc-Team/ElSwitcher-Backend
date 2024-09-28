from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError
from models import Jugador

def get_movimientos_jugador(db: Session, partida_id: int, jugador_id: int):
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    movimientos_del_jugador = jugador.mano_movimientos
    return movimientos_del_jugador
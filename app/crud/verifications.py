from sqlalchemy.orm import Session

from crud.exceptions import PartidaNotFoundError, PartidaLlenaError
from models.jugadores import Jugador
from schemas.jugadores import JugadorData
from models.partidas import Partida
from schemas.partidas import PartidaData

def verificar_partida_existente(db: Session, partida_id: int):
    """Verifica si una partida existe en la base de datos.

    Args:
        db (Session): La sesión de la base de datos.
        partida_id (int): El ID de la partida a verificar.

    Raises:
        PartidaNotFoundError: Si la partida no se encuentra.
    """
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if not partida:
        raise PartidaNotFoundError(partida_id)

def verificar_partida_con_espacio(db: Session, partida_id: int):
    """Verifica si hay espacio disponible en la partida.

    Args:
        db (Session): La sesión de la base de datos.
        partida_id (int): El ID de la partida a verificar.

    Raises:
        PartidaLlenaError: Si la partida está llena.
    """
    MAX_JUGADORES = 4
    numero_jugadores = db.query(Jugador).filter(Jugador.partida_id == partida_id).count()
    if (numero_jugadores >= MAX_JUGADORES):
        raise PartidaLlenaError(partida_id, MAX_JUGADORES)
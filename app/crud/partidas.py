from sqlalchemy.orm import Session

from models.partidas import Partida
from schemas.partidas import PartidaData

"""
    WARNING: Estas funciones no están implementadas, solo están para estructurar el esqueleto del repositorio.
"""

def get_partidas(db: Session):
    return []

def get_partida_by_id(db: Session, id: int):
    return []

def get_partidas_by_name(db: Session, nombre: str):
    return []

def create_partida(db: Session, partida: PartidaData):
    return []

def delete_partida(db: Session, id: int):
    return []
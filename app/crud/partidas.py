from sqlalchemy.orm import Session

from models.partidas import Partida
from schemas.partidas import PartidaData

"""
  WARNING: Estas funciones no están implementadas, solo están para estructurar el esqueleto del repositorio.
"""

def get_partidas(db: Session):
    return db.query(Partida).all()

def get_partida_by_id(db: Session, id: int):
    return db.query(Partida).filter(Partida.id == id).first()

def create_partida(db: Session, partida: PartidaData):
    new_partida = Partida(nombre_partida=partida.nombre_partida, nombre_creador=partida.nombre_creador ,iniciada=False)
    db.add(new_partida)
    db.commit()
    db.flush()
    return new_partida

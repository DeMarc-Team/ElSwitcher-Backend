from sqlalchemy.orm import Session

from models.partidas import Partida
from schemas.partidas import PartidaData

"""
    WARNING: Estas funciones no están implementadas, solo están para estructurar el esqueleto del repositorio.
"""

def get_partidas(db: Session):
    return db.query(Partida).all()

def create_partida(db: Session, partida: PartidaData):
    new_partida = Partida(nombre=partida.nombre, iniciada=False)
    db.add(new_partida)
    db.commit()
    db.flush()
    return new_partida

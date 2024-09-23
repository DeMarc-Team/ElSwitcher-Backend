from sqlalchemy.orm import Session

from crud.exceptions import PartidaNotFoundError
from models import Partida
from schemas import PartidaData
from models import Jugador

def get_partidas(db: Session):
    return db.query(Partida).all()

def get_partida_details(db: Session, id: int):
    partidaDetails = db.query(Partida).filter(Partida.id == id).first()
    if (not partidaDetails):
        raise PartidaNotFoundError(id)
    
    return partidaDetails

def create_partida(db: Session, partida: PartidaData):
    new_partida = Partida(nombre_partida=partida.nombre_partida, nombre_creador=partida.nombre_creador)
    db.add(new_partida)
    db.flush()
    print(f"Id partida creada: {new_partida.id}")
    new_jugador = Jugador(nombre=partida.nombre_creador, es_creador=True, partida_id=new_partida.id)
    db.add(new_jugador)
    db.commit()
    db.flush()
    return new_partida

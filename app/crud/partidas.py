from sqlalchemy.orm import Session
from sqlalchemy import func, select

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida
from schemas import PartidaData
from models import Jugador
from models import Juego
from models import CartaFigura, random_figura
from models import CartaMovimiento

def get_id_creador(db: Session, partida_id):
    jugador = db.query(Jugador).filter((Jugador.es_creador == True) & (Jugador.partida_id == partida_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    return jugador.id_jugador

def get_partidas(db: Session):
    subquery = (
        db.query(Partida.id, func.count(Partida.jugadores).label('jugadores_count'))
        .outerjoin(Partida.jugadores)
        .group_by(Partida.id)
    ).subquery()

    return db.query(Partida).join(subquery, Partida.id == subquery.c.id).filter(
        Partida.iniciada == False,
        subquery.c.jugadores_count < 4
    ).all()

def get_partida_details(db: Session, id: int):
    partidaDetails = db.query(Partida).filter(Partida.id == id).first()
    if (not partidaDetails):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
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

def iniciar_partida(db: Session, id: int):
    partida = db.query(Partida).filter(Partida.id == id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
    
    if (partida.juego or partida.iniciada):
        raise ForbiddenError(f"La partida con ID {id} ya está iniciada.")
    
    if (not len(partida.jugadores) > 1):
        raise ForbiddenError(f"Partida con ID {id} no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.")
    
    id_creador = get_id_creador(db, id)
    new_juego = Juego(turno=id_creador, partida_id=partida.id, partida=partida)


    db.add(new_juego)
    partida.iniciada = True
    repartir_cartas_figura(db, partida)
    repartir_cartas_movimiento(db, partida)
    db.commit()
    db.flush()

def get_cartas_figura_jugador(db: Session, partida_id, jugador_id):
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    mazo_del_jugador = jugador.mazo_cartas_de_figura

    return mazo_del_jugador

def repartir_cartas_figura(db: Session, partida, n_cartas_por_jugador=3):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador):
            new_carta = CartaFigura(figura=random_figura(), jugador_id=jugador.id_jugador)
            db.add(new_carta)
    
def repartir_cartas_movimiento(db: Session, partida, n_cartas_por_jugador=3):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador):
            new_carta = CartaMovimiento(jugador_id=jugador.id_jugador)
            db.add(new_carta)
            
    db.commit()
    db.flush()
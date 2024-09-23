from sqlalchemy.orm import Session

from crud.exceptions import PartidaNotFoundError, PartidaYaIniciada, JuegoNotFoundError
from models import Partida
from schemas import PartidaData
from models import Jugador
from models import Juego
from models import CartaFigura, random_figura

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

def iniciar_partida(db: Session, id: int):
    partida = db.query(Partida).filter(Partida.id == id).first()
    if (not partida):
        raise PartidaNotFoundError(id)
    
    if (partida.juego):
        raise PartidaYaIniciada(id)
    
    id_creador = db.query(Jugador).filter((Jugador.es_creador == True) & (Jugador.partida_id == id)).first().id_jugador
    new_juego = Juego(turno=id_creador, partida_id=partida.id, partida=partida)

    for jugador in partida.jugadores: # TODO: Buscar un mejor lugar para hacer esto o mdoularizarlo
        for i in range(4):
            new_carta = CartaFigura(figura=random_figura(), jugador_id=jugador.id_jugador)
            db.add(new_carta)

    db.add(new_juego)
    partida.iniciada = True
    db.commit()
    db.flush()
    
def get_juego_details(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise PartidaNotFoundError(partida_id)
    
    juego = partida.juego[0]
    if (not juego):
        raise JuegoNotFoundError(partida_id)
    
    return juego

def get_cartas_jugador(db: Session, partida_id, jugador_id):
    player = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    print(player.mazo_cartas_de_figura)
    # TODO: Hacer que esta función retorne únicamente las cartas de figura del jugadorw
    return db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first().mazo_cartas_de_figura
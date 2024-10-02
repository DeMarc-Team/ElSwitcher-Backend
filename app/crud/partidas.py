from sqlalchemy.orm import Session
from sqlalchemy import func
from random import shuffle

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida
from schemas import PartidaData
from models import Jugador
from models import CartaFigura
from models import CartaMovimiento
from schemas import TurnoDetails

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
    new_jugador = Jugador(nombre=partida.nombre_creador, es_creador=True, partida_id=new_partida.id)
    db.add(new_jugador)
    db.commit()
    return new_partida

def iniciar_partida(db: Session, id: int):
    partida = db.query(Partida).filter(Partida.id == id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {id} no encontrada.")
    
    if (partida.iniciada):
        raise ForbiddenError(f"La partida con ID {id} ya está iniciada.")
    
    # if (not len(partida.jugadores) > 1):
    #     raise ForbiddenError(f"Partida con ID {id} no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.")
    #TODO: Hola soy el if de arriba, el emi me comentó debuggeando, si me ven comentado, es porque el muy imbecil se olvido -emi.
    
    partida.iniciada = True
    repartir_cartas_figura(db, partida,3,3)
    repartir_cartas_movimiento(db, partida)
    db.flush()
    shuffle(partida.jugadores)
    db.commit()

def get_cartas_figura_jugador(db: Session, partida_id, jugador_id):
    
    partida = get_partida_details(db, partida_id) # raises ResourceNotFoundError if not found
    
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    mazo_del_jugador = jugador.mazo_cartas_de_figura

    return mazo_del_jugador

def repartir_cartas_figura(db: Session, partida, n_cartas_por_jugador=3, n_cartas_reveladas=2):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador-n_cartas_reveladas):
            new_carta = CartaFigura(jugador_id=jugador.id_jugador, revelada=False)
            db.add(new_carta)

        for i in range(n_cartas_reveladas):
            new_carta = CartaFigura(jugador_id=jugador.id_jugador, revelada=True)
            db.add(new_carta)
    
def repartir_cartas_movimiento(db: Session, partida, n_cartas_por_jugador=3):
    for jugador in partida.jugadores:
        for i in range(n_cartas_por_jugador):
            new_carta = CartaMovimiento(jugador_id=jugador.id_jugador)
            db.add(new_carta)

def abandonar_partida(db: Session, partida_id: int, jugador_id: int):
    partida = get_partida_details(db, partida_id) # raises ResourceNotFoundError if not found
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")

    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    partida_iniciada = partida.iniciada or partida.juego != []
    jugador_es_creador = jugador.id_jugador == partida.id_creador or jugador.es_creador == True
    
    if (jugador_es_creador and not partida_iniciada):
        raise ForbiddenError(f"El creador con ID {jugador_id} no puede abandonar la partida con ID {partida_id} antes de iniciarla.")
    
    db.delete(jugador)
    partida.jugadores.remove(jugador)
    db.flush()

    if (len(partida.jugadores) <= 1 and partida_iniciada):
        # TODO: Declarar ganador al jugador que queda
        db.delete(partida)    
    db.commit()


def get_tablero(db: Session, partida_id: int):
    partida = db.query(Partida).filter(Partida.partida_id == partida_id).first()

    if (partida == None): # Si no hay juego, devolver un tablero vacío
        raise ResourceNotFoundError(f"Partida no encontrada")

    return partida.tablero


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
    
    if (not partida.iniciada):
        raise ForbiddenError(f"La partida con ID {partida_id} todavía no comenzó.")
    
    juego = partida.juego[0]
    
    nombre_jugador_del_turno = juego.jugador_del_turno.nombre
    
    turno_details = TurnoDetails( # TODO: En vez de hacerlo aca al formato, quizas deberia hacerse en el router
        id_jugador=juego.jugador_id,
        nombre_jugador=nombre_jugador_del_turno
    )
    
    return turno_details
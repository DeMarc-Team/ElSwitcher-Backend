from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador
from schemas import TurnoDetails, CasillasMov


def get_movimientos_jugador(db: Session, partida_id: int, jugador_id: int):
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (
        Jugador.id_jugador == jugador_id)).first()

    if (not jugador):
        raise ResourceNotFoundError(
            f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")

    movimientos_del_jugador = jugador.mano_movimientos
    return movimientos_del_jugador


def get_turno_details(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {partida_id} todavía no comenzó.")

    nombre_jugador_del_turno = partida.jugador_del_turno.nombre

    turno_details = TurnoDetails(
        id_jugador=partida.jugador_id,
        nombre_jugador=nombre_jugador_del_turno
    )

    return turno_details


def siguiente_turno(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {partida_id} todavía no comenzó.")

    partida.jugadores.append(partida.jugadores.pop(0))
    db.flush()
    for jugador in partida.jugadores:
        jugador.orden = partida.jugadores.index(jugador)

    db.commit()
    # return actual_jugador.id_jugador # Aca va el ID del jugador que tiene o tenía el turno??


def terminar_turno(db: Session, partida_id, jugador_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {partida_id} todavía no comenzó.")

    actual_jugador = partida.jugador_del_turno

    if (actual_jugador.id_jugador != jugador_id):
        raise ForbiddenError(
            f"El ID del jugador que posee el turno no es {jugador_id}.")

    siguiente_turno(db, partida_id)

    db.commit()


def get_tablero(db: Session, partida_id: int):
    juego = db.query(Partida).filter(Partida.id == partida_id).first()

    if (juego == None):
        raise ResourceNotFoundError(f"Partida no encontrada")

    return juego.tablero


def modificar_casillas(id_partida: int, id_jugador: int, coordenadas: CasillasMov, db: Session):
    juego = db.query(Partida).filter(Partida.id == id_partida).first()

    if (juego == None):
        raise ResourceNotFoundError(f"Partida no encontrada")
    
    import json
    tablero_deserealizado = json.loads(juego.tablero)

    from movimientos import swapear_en_tablero, SET_DE_MOVIMIENTOS
    
    origen = casilla_to_tuple(coordenadas.casilla1)
    destino = casilla_to_tuple(coordenadas.casilla2)

    print(origen)

    mov = next((carta for carta in SET_DE_MOVIMIENTOS if carta.movimiento == coordenadas.codeMove), None)
    if not mov:
        raise ResourceNotFoundError(f"Movimiento con codeMove {coordenadas.codeMove} no encontrado")
    if not swapear_en_tablero(mov,tablero_deserealizado,origen,destino):
        db.rollback
        raise ForbiddenError("Movimiento no permitido")
    
    juego.tablero = json.dumps(tablero_deserealizado)
    db.commit()


def casilla_to_tuple(casilla):
    return (int(casilla.row) ,int(casilla.col))

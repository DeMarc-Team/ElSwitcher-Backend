from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador, CartaMovimiento, MovimientoParcial
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
    
    limpiar_stack_movimientos_parciales(db, partida_id)
    
    from crud.partidas import reponer_cartas_movimiento
    reponer_cartas_movimiento(db, actual_jugador)

    siguiente_turno(db, partida_id)

    db.commit()

def limpiar_stack_movimientos_parciales(db, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")
    
    while partida.movimientos_parciales:
        deshacer_movimiento(db, partida_id)
    db.commit()


def get_tablero(db: Session, partida_id: int):
    juego = db.query(Partida).filter(Partida.id == partida_id).first()

    if (juego == None):
        raise ResourceNotFoundError(f"Partida no encontrada")

    return juego.tablero


def modificar_casillas(id_partida: int, id_jugador: int, coordenadas_y_carta: CasillasMov, db: Session):
    from movimientos import swapear_en_tablero, is_valid_move
    import json

    juego = db.query(Partida).filter(Partida.id == id_partida).first()

    if (juego == None): # Esto no habria que comporbarlo si crud tuviera un buen metodo get_juego
        raise ResourceNotFoundError(f"Partida no encontrada")
    
    if (juego.jugador_del_turno.id_jugador != id_jugador):
        raise ForbiddenError("No es el turno del jugador")
    

    tablero_deserealizado = json.loads(juego.tablero)

    origen, destino, mov = desempaquetar_coords(coordenadas_y_carta)
    moveCode = mov.movimiento
    
    if not card_is_available(juego.jugador_del_turno,moveCode): # El jugador posee la carta?
        raise ForbiddenError("El player no posee esa carta")

    if not is_valid_move(mov,tablero_deserealizado,origen,destino): # El movimiento es uno valido?
        raise ForbiddenError("Movimiento no permitido")
    
    carta = None
    for c in juego.jugador_del_turno.mano_movimientos:
        if c.movimiento == moveCode and not c.usada_en_movimiento_parcial:
            carta = c
            break

    if not carta:
        raise ResourceNotFoundError(f"Carta de movimiento no encontrada o ya usada por el jugador con ID {id_jugador}.")

    carta_id = carta.id

    push_movimiento_parcial(db, id_partida, carta_id, origen, destino)

    swapear_en_tablero(tablero_deserealizado,origen,destino)
    
    juego.tablero = json.dumps(tablero_deserealizado)
    db.commit()

def card_is_available(jugador: Jugador, movimiento):
    for carta in jugador.mano_movimientos:
        if carta.movimiento == movimiento and not carta.usada_en_movimiento_parcial:
            return True
    
    return False

def desempaquetar_coords(coordenadas_y_carta):
    origen = casilla_to_tuple(coordenadas_y_carta.casilla1)
    destino = casilla_to_tuple(coordenadas_y_carta.casilla2)
    mov = matchear_obtener_carta(coordenadas_y_carta.codeMove)
    return origen,destino,mov

def matchear_obtener_carta(codigo_movimiento):
    from movimientos import SET_DE_MOVIMIENTOS
    mov = next((carta for carta in SET_DE_MOVIMIENTOS if carta.movimiento == codigo_movimiento), None)
    if not mov:
        raise ResourceNotFoundError(f"Movimiento con codeMove {codigo_movimiento} no encontrado")
    return mov

def casilla_to_tuple(casilla):
    return (int(casilla.row) ,int(casilla.col))

def push_movimiento_parcial(db: Session, partida_id, carta_id, origen, destino):
    '''
    Agrega un movimiento a la lista de movimientos parciales del jugador.
    '''
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    carta = db.query(CartaMovimiento).filter(CartaMovimiento.id == carta_id).first()
    if (not carta):
        raise ResourceNotFoundError(f"Carta de movimiento con ID {carta_id} no encontrada.")
    
    orden = len(partida.movimientos_parciales)

    movimiento_parcial = MovimientoParcial(
        carta_id=carta_id,
        origen=str(origen),
        destino=str(destino),
        carta=carta,
        partida_id=partida_id,
        orden=orden
    )

    partida.movimientos_parciales.append(movimiento_parcial)

    db.commit()

def deshacer_movimiento(db: Session, id_partida):
    partida = db.query(Partida).filter(Partida.id == id_partida).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {id_partida} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {id_partida} todavía no comenzó.")

    movimientos_parciales = partida.movimientos_parciales
    if (len(movimientos_parciales) == 0):
        raise ForbiddenError(
            f"No hay movimientos parciales para deshacer en la partida con ID {id_partida}.")

    ultimo_movimiento = movimientos_parciales.pop()

    import ast
    origen = ast.literal_eval(ultimo_movimiento.origen) # Estas tuplas se guardan como strings en la base de datos
    destino = ast.literal_eval(ultimo_movimiento.destino)

    from movimientos import swapear_en_tablero
    import json

    tablero = json.loads(partida.tablero)
    swapear_en_tablero(tablero, origen, destino)
    partida.tablero = json.dumps(tablero)

    db.delete(ultimo_movimiento)

    db.commit()
    return ultimo_movimiento

def get_movimientos_parciales(db: Session, id_partida):
    partida = db.query(Partida).filter(Partida.id == id_partida).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {id_partida} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {id_partida} todavía no comenzó.")

    movimientos_parciales = partida.movimientos_parciales
    return movimientos_parciales
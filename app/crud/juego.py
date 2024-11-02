from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador, CartaMovimiento, MovimientoParcial
from schemas import TurnoDetails, CasillasMov, CompletarFiguraData
from figuras import hallar_todas_las_figuras_en_tablero
from constantes_juego import N_FIGURAS_REVELADAS
from crud.TemporizadorTurno import temporizadores_turno

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


def siguiente_turno(db: Session, partida_id, atomic=True):
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

    if atomic:
        db.commit()
    else:
        db.flush()

def reponer_cartas_movimiento(db: Session, partida: Partida, jugador: Jugador, n_cartas_por_jugador=3, atomic=True):
    '''
    Procedimiento para reponer las cartas movimiento de un jugador.
    
    Repone hasta que el jugador tenga n_cartas_por_jugador en la mano.
    '''
    
    cantidad_movimientos = len(jugador.mano_movimientos)

    # Reponemos las cartas de movimiento del jugador
    for i in range(0, n_cartas_por_jugador - cantidad_movimientos):
        new_carta = CartaMovimiento(jugador_id=jugador.id_jugador)
        db.add(new_carta)
        
    if atomic:
        db.commit()
    else:
        db.flush()

def reponer_cartas_figura(db: Session, partida: Partida, jugador: Jugador, n_reveladas=N_FIGURAS_REVELADAS, atomic=True):
    '''
    Procedimiento para reponer las cartas figura de un jugador.
    
    Repone hasta que el jugador tenga n_reveladas en la mano.
    '''
    
    cartas_no_reveladas = [carta for carta in jugador.mazo_cartas_de_figura if not carta.revelada]
    cantidad_reveladas = len([carta for carta in jugador.mazo_cartas_de_figura if carta.revelada])
    cartas_a_revelar = min(len(cartas_no_reveladas), n_reveladas - cantidad_reveladas)

    for i in range(cartas_a_revelar):
        cartas_no_reveladas[i].revelada = True
    
    if atomic:
        db.commit()
    else:
        db.flush()

def terminar_turno(db: Session, partida_id, jugador_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")

    validar_turno_jugador(db, partida_id, jugador_id)
    
    temporizadores_turno.cancelar_temporizador_del_turno(partida_id)
    
    limpiar_stack_movimientos_parciales(db, partida_id, atomic=False)
    
    reponer_cartas_movimiento(db, partida, partida.jugador_del_turno, atomic=False)
    reponer_cartas_figura(db, partida, partida.jugador_del_turno, atomic=False)
    db.flush()
    siguiente_turno(db, partida_id, atomic=False)

    db.commit()

def validar_turno_jugador(db: Session, partida_id, jugador_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")
    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {partida_id} todavía no comenzó.")

    actual_jugador = partida.jugador_del_turno

    if (actual_jugador.id_jugador != jugador_id):
        raise ForbiddenError(f"El ID del jugador que posee el turno no es {jugador_id}.")

def limpiar_stack_movimientos_parciales(db, partida_id, atomic=True):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {partida_id} no encontrada.")
    
    while partida.movimientos_parciales:
        deshacer_movimiento(db, partida_id, atomic=False)
    
    if atomic:
        db.commit()
    else:
        db.flush()


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

    push_movimiento_parcial(db, id_partida, carta_id, origen, destino, atomic=False)

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

def push_movimiento_parcial(db: Session, partida_id, carta_id, origen, destino, atomic=True):
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

    if atomic:
        db.commit()
    else:
        db.flush()

def deshacer_movimiento(db: Session, id_partida, atomic=True):
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

    if atomic:
        db.commit()
    else:
        db.flush()

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

def get_figuras_en_tablero(partida: Partida):
    '''
    Calcula y retorna todas las figuras formadas encontradas en el tablero.
    '''    

    import json
    tablero = partida.tablero
    tablero_decodificado = json.loads(tablero)

    return hallar_todas_las_figuras_en_tablero(tablero_decodificado)

def completar_figura_propia(db: Session, id_partida: int, id_jugador: int, figura_data: CompletarFiguraData):
    partida = db.get(Partida, id_partida)
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {id_partida} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {id_partida} todavía no comenzó.")
    
    jugador = db.get(Jugador, id_jugador)
    if (not jugador):
        raise ResourceNotFoundError(
            f"Jugador con ID {id_jugador} no encontrado en la partida con ID {id_jugador}.")
    
    if (jugador.id_jugador != partida.jugador_id):
        raise ForbiddenError(
            f"El jugador con ID {jugador.id_jugador} no posee el turno."
        )
    
    hay_ganador = unatomic_usar_figura(db, partida, jugador, figura_data)
    if (not hay_ganador.get("hay_ganador")):
        unatomic_aplicar_parciales(db, partida)
    db.commit()
    return hay_ganador

def unatomic_usar_figura(db: Session, partida: Partida, jugador: Jugador, figura_data: CompletarFiguraData):    

    carta_fig_deseada = figura_data.carta_fig
    cartas_a_usar = next((carta for carta in jugador.mazo_cartas_de_figura if (carta.revelada and carta.figura == carta_fig_deseada)), None)
    
    if (not cartas_a_usar):
        raise ResourceNotFoundError(
            f"El jugador no tiene en la mano ninguna carta de figura revelada del formato {carta_fig_deseada}."
        )
    
    figuras_en_tablero = get_figuras_en_tablero(partida)
    
    if (carta_fig_deseada not in figuras_en_tablero.keys()):
        raise ResourceNotFoundError(
            f"No existe (en el tablero) ninguna figura del tipo que se intenta utilizar."
        )
    
    coords_figuras_del_tipo = figuras_en_tablero[carta_fig_deseada]
    coords_figura = casillas_to_coords_figura_set(figura_data.figura)
    
    if (coords_figura not in coords_figuras_del_tipo):
        raise ResourceNotFoundError(
            f"No existe (en el tablero) la figura que se intenta utilizar en las coordenadas enviadas."
        )
    
    db.delete(cartas_a_usar)
    db.flush()
    from crud.partidas import hay_ganador
    return hay_ganador(db, partida)
    
    

def unatomic_aplicar_parciales(db: Session, partida: Partida):
    '''
    Aplica los movimientos parciales del jugador (NO HACE VERIFICACIONES DE PERMISOS, i.e, QUE EL JUGADOR TENGA EL TURNO).
    '''
    
    movimientos_parciales = partida.movimientos_parciales
    movimientos_parcializados = [parcial.carta for parcial in movimientos_parciales]
    
    for parcial in movimientos_parciales:
        db.delete(parcial)
    
    for movimiento in movimientos_parcializados:
        db.delete(movimiento)
        
    db.flush()


def casillas_to_coords_figura_set(casillas_figura):
    '''
    Convierte una lista de casillas en un conjunto de tuplas con sus equivalentes coordenadas.
    
    Por ejemplo:
    
    [{row: row_value1, col: col_value1}], [{row: row_value2, col: col_value2}] -> {(row_value1, col_value1), (row_value2, col_value2)}
    '''
    
    return set((casilla.row, casilla.col) for casilla in casillas_figura)

def get_cartas_figura_jugador(db: Session, partida_id, jugador_id):
    
    from crud.partidas import get_partida_details # FIXME: arreglar esta chanchada con el repository
    partida = get_partida_details(db, partida_id) # raises ResourceNotFoundError if not found
    
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (Jugador.id_jugador == jugador_id)).first()
    if (not jugador):
        raise ResourceNotFoundError(f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")
    
    mano_del_jugador = [figura_revelada for figura_revelada in jugador.mazo_cartas_de_figura if figura_revelada.revelada]

    return mano_del_jugador

def get_id_jugador_turno(db: Session, partida_id):
    partida = db.query(Partida).filter(Partida.id == partida_id).first()
    if (not partida):
        raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
    
    return partida.jugador_id
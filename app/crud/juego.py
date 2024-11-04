from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador, CartaMovimiento, MovimientoParcial
from schemas import Casilla, CasillasMov, CompletarFiguraData, BloquearFiguraData
from figuras import hallar_todas_las_figuras_en_tablero

def get_movimientos_jugador(db: Session, partida_id: int, jugador_id: int):
    jugador = db.query(Jugador).filter((Jugador.partida_id == partida_id) & (
        Jugador.id_jugador == jugador_id)).first()

    if (not jugador):
        raise ResourceNotFoundError(
            f"Jugador con ID {jugador_id} no encontrado en la partida con ID {partida_id}.")

    movimientos_del_jugador = jugador.mano_movimientos
    return movimientos_del_jugador

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
    partida = get_partida(db, id_partida)
    jugador = get_jugador(db, partida, id_jugador)
    
    if (jugador.id_jugador != partida.jugador_id):
        raise ForbiddenError(
            f"El jugador con ID {jugador.id_jugador} no posee el turno."
        )
    
    ganador = unatomic_usar_figura(db, partida, jugador, figura_data)
    if (not ganador.get("hay_ganador")):
        unatomic_aplicar_parciales(db, partida)
    db.commit()
    return ganador

def bloquear_carta_ajena(db: Session, id_partida: int, id_jugador: int, bloqueo_data: BloquearFiguraData):
    partida = get_partida(db, id_partida)
    jugador = get_jugador(db, partida, id_jugador)
        
    unatomic_bloquear_figura(db, partida, jugador, bloqueo_data)
    unatomic_aplicar_parciales(db, partida)
    db.commit()
 
def unatomic_usar_figura(db: Session, partida: Partida, jugador: Jugador, figura_data: CompletarFiguraData):    

    carta_fig_deseada = figura_data.carta_fig
    coordenadas_fig_deseada = figura_data.figura
    carta_a_usar = get_carta_revelada_from_jugador(jugador, carta_fig_deseada)
    check_figura_en_tablero(partida, coordenadas_fig_deseada, carta_fig_deseada)
    
    db.delete(carta_a_usar)
    db.flush()
    from crud.partidas import hay_ganador
    return hay_ganador(db, partida.id)
       
def unatomic_bloquear_figura(db: Session, partida: Partida, jugador: Jugador, bloqueo_data: BloquearFiguraData):
    """
    Recibe una partida, un jugador y datos para bloquear a otro jugador y
    en caso de poder hacerlo según las reglas del juego, bloquea la carta de este último.
    """
    
    if (jugador.id_jugador != partida.jugador_id):
        raise ForbiddenError(
            f"El jugador con ID {jugador.id_jugador} no posee el turno."
        )
    
    fig_deseada = bloqueo_data.carta_fig
    coordenadas_fig_deseada = bloqueo_data.figura
    
    jugador_a_bloquear = get_jugador(db, partida, bloqueo_data.id_jugador_bloqueado)
    
    if ( jugador_a_bloquear.bloqueado ):
        raise ForbiddenError(
            f"El jugador con ID {jugador_a_bloquear.id} ya posee una carta bloqueada."    
        )
    
    if ( len(jugador_a_bloquear.mano_figuras) == 1 ):
        raise ForbiddenError(
            f"El jugador con ID {jugador_a_bloquear.id} tiene una única carta de figura en su mano."    
        )
    
    carta_a_bloquear = get_carta_revelada_from_jugador(jugador_a_bloquear, fig_deseada)
    check_figura_en_tablero(partida, coordenadas_fig_deseada, fig_deseada)
    
    carta_a_bloquear.bloqueada = True
    jugador_a_bloquear.bloqueado = True
    db.flush()

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

def get_partida(db: Session, id_partida: int):
    partida = db.get(Partida, id_partida)
    if (not partida):
        raise ResourceNotFoundError(
            f"Partida con ID {id_partida} no encontrada.")

    if (not partida.iniciada):
        raise ForbiddenError(
            f"La partida con ID {id_partida} todavía no comenzó.")
            
    return partida

def get_jugador(db: Session, partida: Partida, id_jugador: int):
    jugador = db.get(Jugador, id_jugador)
    if ((not jugador) or (jugador not in partida.jugadores)):
        raise ResourceNotFoundError(
            f"Jugador con ID {id_jugador} no encontrado en la partida con ID {partida.id}.")
        
    return jugador

def check_figura_en_tablero(partida: Partida, coordenadas_fig_deseada: list[Casilla], fig_deseada: str):
    """
    Verifica que la figura con código fig_deseada esté en las coordenadas del tablero coordenadas_fig_deseada.
    En caso de no estarlo, arroja la excepción ResourceNotFoundError.
    """
    
    figuras_en_tablero = get_figuras_en_tablero(partida)
    
    if (fig_deseada not in figuras_en_tablero.keys()):
        raise ResourceNotFoundError(
            f"No existe (en el tablero) ninguna figura del tipo que se intenta utilizar."
        )
    
    coords_figuras_del_tipo = figuras_en_tablero[fig_deseada]
    coords_figura = casillas_to_coords_figura_set(coordenadas_fig_deseada)
    
    if (coords_figura not in coords_figuras_del_tipo):
        raise ResourceNotFoundError(
            f"No existe (en el tablero) la figura que se intenta utilizar en las coordenadas enviadas."
        )

def get_carta_revelada_from_jugador(jugador: Jugador, fig_deseada: str):
    cartas_del_tipo_en_mano = [carta for carta in jugador.mano_figuras if carta.figura == fig_deseada]
    
    if (cartas_del_tipo_en_mano == []):
        raise ResourceNotFoundError(
            f"El jugador de ID {jugador.id} no tiene en la mano ninguna carta de figura revelada del formato {fig_deseada}."
        )
    
    cartas_del_tipo_libres = [carta for carta in cartas_del_tipo_en_mano if not carta.bloqueada]
    
    if (cartas_del_tipo_libres == []):
        raise ForbiddenError(
            f"El jugador de ID {jugador.id} no tiene ninguna carta del formato {fig_deseada} desbloqueada en su mano."
        )
    
    carta_a_usar = cartas_del_tipo_libres[0]
    
    return carta_a_usar

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
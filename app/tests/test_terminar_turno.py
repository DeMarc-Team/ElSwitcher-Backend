import mock
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida, consumir_carta_movimiento, consumir_carta_figura_reveladas
from websockets_manager.ws_partidas_manager import ACTUALIZAR_TURNO, ACTUALIZAR_TABLERO
import pytest
from tools import get_all_tables, capturar_metadata as capturar, comparar_capturas, verificar_diccionarios

@pytest.mark.parametrize("numero_de_jugadores", [2, 3, 4])
@pytest.mark.parametrize("numero_de_reveadas", [0, 1, 2])
def test_terminar_turno_yreponer_figuras(test_db, test_ws, numero_de_jugadores, numero_de_reveadas):
    '''
    Test que chequea que al terminar el turno de un jugador, se reponen las figuras reveladas que se descartaron.
    '''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws[ACTUALIZAR_TURNO] = 1
    test_ws[ACTUALIZAR_TABLERO] = 1

    # Inicializamos la precondicion
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=numero_de_jugadores-1)
    iniciar_partida(test_db, partida)
    jugador_inicial = partida.jugador_del_turno
    consumir_carta_figura_reveladas(test_db, jugador_inicial, cantidad=3-numero_de_reveadas)

    # Realizamos la petición
    numero_de_figuras_reveladas = len([figura for figura in jugador_inicial.mazo_cartas_de_figura if figura.revelada])
    assert numero_de_figuras_reveladas < 3, f"Fallo de precondición: Se esperaba que el jugador tuviera menos de 3 figuras reveladas, pero tiene {numero_de_figuras_reveladas}."
    captura_inicial = capturar(get_all_tables(test_db))
    
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    test_db.refresh(partida) # Para actualizar localmente la info de la partida
    test_db.refresh(jugador_inicial) # Para actualizar localmente la info del jugador
    captura_final = capturar(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # Verificamos que se hayan reinsertado las figuras
    numero_de_figuras_reveladas = len([figura for figura in jugador_inicial.mazo_cartas_de_figura if figura.revelada])
    numero_esperado = min(3,len(jugador_inicial.mazo_cartas_de_figura))
    assert numero_de_figuras_reveladas == numero_esperado, f"Fallo: Se esperaba que el jugador tuviera {numero_esperado} figuras reveladas, pero tiene {numero_de_figuras_reveladas}."
    assert not eliminadas, f"Fallo: Se esperaba que no se eliminara ninguna tabla, pero se eliminaron {eliminadas}."
    assert not creadas, f"Fallo: Se esperaba que no se creara ninguna tabla, pero se crearon {creadas}."
    modificaciones_esperadas_en = {'jugadores': ['orden'], 'cartas_de_figura': ['revelada']}
    assert verificar_diccionarios(modificaciones, modificaciones_esperadas_en), f"Fallo: Las modificaciones no fueron las esperadas."

def test_terminar_turno(test_db, test_ws):
    '''Test que chequea el funcionamiento en el escenario exitoso del endpoint para terminar_turno.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    jugador_inicial = partida.jugador_del_turno
    segundo_jugador = partida.jugadores[1]

    # Construyo una copia de los valores que deben permanecer invariantes
    partida_datos_invariantes = {
        "id": partida.id,
        "nombre_partida": partida.nombre_partida,
        "nombre_creador": partida.nombre_creador,
        "iniciada": partida.iniciada,
        "tablero": str(partida.tablero),
        "id_creador": partida.id_creador
    }

    # Pasamos el turno
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_inicial.id_jugador}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    test_db.refresh(partida) # Para actualizar localmente la info de la partida

    partida_datos_posteriores = {
        "id": partida.id,
        "nombre_partida": partida.nombre_partida,
        "nombre_creador": partida.nombre_creador,
        "iniciada": partida.iniciada,
        "tablero": str(partida.tablero),
        "id_creador": partida.id_creador
    }

    # Comprobamos que se mantengan los datos invariantes
    assert (
        partida_datos_invariantes == partida_datos_posteriores
    ), f"Fallo: Se esperaba que el único dato que se modificara de la partida fuera el orden, pero no es así."

    # Comprobamos que el turno sea del jugador correspondiente
    assert (
        partida.jugador_del_turno.id_jugador == segundo_jugador.id_jugador
    ), f"Fallo: Se esperaba que el nuevo jugador del turno fuera el de id {segundo_jugador.id_jugador}, pero tiene id {partida.jugador_del_turno.id_jugador}."
    
    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = 1
    test_ws[ACTUALIZAR_TABLERO] = 1

def test_vuelta_completa(test_db, test_ws):
    '''Test que chequea el funcionamiento de una vuelta completa de turnos.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Pasamos una ronda completa de turnos
    orden_de_turnos = pasar_ronda_completa(test_db, partida)
    id_jugador_inicial = orden_de_turnos[0]

    # Obtenemos el id del nuevo jugador actual
    id_jugador_final = partida.jugador_id
        
    # Verificamos que los turnos "hayan dado la vuelta completa"
    assert id_jugador_inicial == id_jugador_final, f"Fallo: Se esperaba que el último jugador fuera el mismo que el inicial, pero eso no ocurrió."
    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = len(partida.jugadores)
    test_ws[ACTUALIZAR_TABLERO] = len(partida.jugadores)

def test_varias_rondas(test_db, test_ws):
    '''Test sobre la confiabilidad de los turnos a lo largo de varias rondas.'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Hacemos una primera ronda para identificar el orden por id
    orden_de_turnos = pasar_ronda_completa(test_db, partida)

    # Verificamos que se haya pasado por todos los jugadores
    n_ids_que_jugaron = len(set(orden_de_turnos))
    assert n_ids_que_jugaron == len(
        partida.jugadores
    ), f"Fallo: Se esperaba que se haya pasado por todos los jugadores ({len(partida.jugadores)}, pero solo jugaron {n_ids_que_jugaron}), "

    # Hacemos 4 rondas mas para ver si tal orden se mantiene
    for i in range(0, 4):
        nuevo_orden = pasar_ronda_completa(test_db, partida)
        assert nuevo_orden == orden_de_turnos, "Fallo: El orden de la primera ronda no coincide con el de la ronda con i={i}."

    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = 5 * len(partida.jugadores)
    test_ws[ACTUALIZAR_TABLERO] = 5 * len(partida.jugadores)

def test_reponer_cartas_movimiento(test_db):
    '''Test sobre la reposición de las cartas de movimiento al finalizar el turno del jugador.'''
    
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=2)
    with mock.patch("models.CartaMovimiento.random_movimiento", return_value="m1"):
        iniciar_partida(db=test_db, partida=partida)
    jugador_del_turno = partida.jugador_del_turno

    consumir_carta_movimiento(test_db, jugador_del_turno, "m1", cantidad=2)
    
    with mock.patch("models.CartaMovimiento.random_movimiento", mock.Mock(side_effect=["m2", "m3"])):
        response = client.put(f'juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    
    test_db.refresh(partida) # Para actualizar localmente la info de la partida
    
    movimientos = [mov.movimiento for mov in jugador_del_turno.mano_movimientos]
    
    assert movimientos == [
        "m1", "m2", "m3"
    ], "Fallo: Las cartas de movimiento del jugador no se repusieron como se esperaba."

def test_partida_inexistente_404(test_db, test_ws):
    '''Test sobre los mensajes de error ante el envío de terminar turno a una partida inexistente.'''

    # Intentamos terminar el turno de una partida inexistente.
    response = client.put(f'juego/{999999}/jugadores/{999999}/turno')
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"

def test_partida_no_iniciada_403(test_db, test_ws):
    '''Test sobre los mensajes de error ante el envío de terminar turno a una partida no iniciada.'''

    partida, _ = crear_partida(test_db)

    # Intentamos terminar el turno de una partida no iniciada.
    response = client.put(f'juego/{partida.id}/jugadores/{1}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"

def test_jugador_sin_turno_403(test_db, test_ws):
    '''Test sobre los mensajes de error ante el envío de terminar turno de un jugador que no posee el turno.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    # Intentamos terminar el turno de un jugador que no posee el turno
    response = client.put(f'juego/{partida.id}/jugadores/{3}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"

# Auxiliares
def pasar_ronda_completa(db, partida):
    '''
    Pasa una ronda completa de turnos y retorna una lista ordenada por turno de los ids de los jugadores que jugaron la ronda.
    '''
    
    orden_de_turnos = []
    id_jugador_anterior = None
    # Hacemos una primera ronda para identificar el orden por id
    for i in range(0, len(partida.jugadores)):

        # Obtenemos el id del jugador actual
        id_jugador_actual = partida.jugador_id

        # Verificamos que efectivamente se haya cambiado el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."

        orden_de_turnos.append(id_jugador_actual)
        id_jugador_anterior = id_jugador_actual

        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
        db.refresh(partida) # Para actualizar localmente la info de la partida
        
    return orden_de_turnos
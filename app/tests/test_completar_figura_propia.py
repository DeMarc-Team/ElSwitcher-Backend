import pdb
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida, establecer_tablero, cartear_figuras, listas_to_casillas_figura
from verifications import check_response
from schemas import Casilla
from tools import capturar_metadata, comparar_capturas_metadata

def test_usar_figura_propia(test_db):
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)
    jugador_del_turno = partida.jugador_del_turno

    # Tablero que deseamos que se utilice
    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]

    # Diccionario con las casillas de las figuras formadas en el tablero del mock
    figuras_formadas_en_mock = {
        "figuras_a_resaltar": {
            "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]]
        }
    }

    establecer_tablero(test_db, partida, tablero_mock)
    cartear_figuras(test_db, jugador_del_turno, ["f1"])

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Chequeamos que se haya consumido la carta correctamente
    cartas_reveladas_restantes = [carta_revelada for carta_revelada in jugador_del_turno.mazo_cartas_de_figura if carta_revelada.revelada]
    assert cartas_reveladas_restantes == [], f"Fallo: Se esperaba que el jugador agotara su única carta, pero le quedan {len(cartas_reveladas_restantes)}."

# ----------------------------------------------------------------

def test_usar_figura_propia_jugador_no_turno_403(test_db, test_ws):
    '''Test de jugador que no es del turno intentando usar una figura propia'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)

    jugador_del_turno = partida.jugador_del_turno
    otro_jugador = partida.jugadores[1]
    assert jugador_del_turno != otro_jugador, "Se cambio models y no se actualizo el test"
    
    # FIXME: Repeticion de codigo, se puede modularizar (No lo hago por si a caso)
    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]
    
    resaltadas_en_el_mock = {
        "figuras_a_resaltar": {
            "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]],
            "f2": [],
            "f3": [],
            "f4": [],
        }
    }
    
    establecer_tablero(test_db, partida, tablero_mock)
    cartear_figuras(test_db, otro_jugador, ["f1"])
    
    casillas_figura = []
    for casilla in resaltadas_en_el_mock["figuras_a_resaltar"]["f1"][0]:
        casillas_figura.append({
            "row": casilla[0],
            "col": casilla[1]
        }
        )
    

    captura_inicial = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura, *otro_jugador.mazo_cartas_de_figura])
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{otro_jugador.id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"El jugador con ID {otro_jugador.id_jugador} no posee el turno."}
    check_response(response, status_code_esperado=403, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura, *otro_jugador.mazo_cartas_de_figura])
    diferencias = comparar_capturas_metadata(captura_inicial, captura_final)

    assert not diferencias, f"Se encontraron modificaciones en la db: {diferencias}"

# ----------------------------------------------------------------

def test_usar_figura_propia_partida_no_existe_404(test_db, test_ws):
    '''Test de jugador que no es del turno intentando usar una figura propia'''
    # Realizamos la petición
    id_partida = 1
    id_jugador = 1
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{id_partida}/jugadores/{id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

# ----------------------------------------------------------------

def test_usar_figura_propia_partida_no_iniciada_403(test_db, test_ws):
    '''Test de jugador que no es del turno intentando usar una figura propia'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    
    jugador = partida.jugadores[0]

    captura_inicial = capturar_metadata([partida, *partida.jugadores, *jugador.mazo_cartas_de_figura])

    # Realizamos la petición
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador.id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"La partida con ID {partida.id} todavía no comenzó."}
    check_response(response, status_code_esperado=403, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador.mazo_cartas_de_figura])
    diferencias = comparar_capturas_metadata(captura_inicial, captura_final)

    assert not diferencias, f"Se encontraron modificaciones en la db: {diferencias}"

# ----------------------------------------------------------------

def test_usar_figura_propia_jugador_no_existe_404(test_db, test_ws):
    '''Test de jugador que no es del turno intentando usar una figura propia'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)
    
    id_jugador = 3

    # Realizamos la petición
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"Jugador con ID {id_jugador} no encontrado en la partida con ID {id_jugador}."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

# ----------------------------------------------------------------

def test_usar_figura_propia_mano_sin_figura_404(test_db, test_ws):
    '''Test de jugador del turno intentando usar una figura propia que no tiene en su mano.'''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)

    jugador_del_turno = partida.jugador_del_turno
    # mockeamos la mano del jugador
    cartear_figuras(test_db, creador, ["f2"])

    captura_inicial = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    # Realizamos la petición
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": "f1"
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"El jugador no tiene en la mano ninguna carta de figura revelada del formato {request_body.get("carta_fig")}."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    diferencias = comparar_capturas_metadata(captura_inicial, captura_final)

    assert not diferencias, f"Se encontraron modificaciones en la db: {diferencias}"

# ----------------------------------------------------------------

def test_usar_figura_propia_no_en_tablero_404(test_db, test_ws):
    '''Test de jugador del turno intentando usar una figura propia que no está en el tablero.'''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)

    jugador_del_turno = partida.jugador_del_turno

    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]

    establecer_tablero(test_db, partida, tablero_mock)
    figura = "f2"
    cartear_figuras(test_db, jugador_del_turno, [figura])

    captura_inicial = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    # Realizamos la petición
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": figura
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"No existe (en el tablero) ninguna figura del tipo que se intenta utilizar."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    diferencias = comparar_capturas_metadata(captura_inicial, captura_final)

    assert not diferencias, f"Se encontraron modificaciones en la db: {diferencias}"

# ----------------------------------------------------------------

def test_usar_figura_propia_casilla_incorrecta_404(test_db,test_ws):
    '''Test de jugador del turno intentando usar una figura propia en una casilla incorrecta.'''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)

    jugador_del_turno = partida.jugador_del_turno

    tablero_mock = [
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]

    establecer_tablero(test_db, partida, tablero_mock)
    figura = "f1"
    cartear_figuras(test_db, creador, [figura])

    captura_inicial = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    # Realizamos la petición
    request_body = {
        "figura": [{"row": 0, "col": 0}],
        "carta_fig": figura
    }
    response = client.put(f'/juego/{partida.id}/jugadores/{creador.id_jugador}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"No existe (en el tablero) la figura que se intenta utilizar en las coordenadas enviadas."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    diferencias = comparar_capturas_metadata(captura_inicial, captura_final)

    assert not diferencias, f"Se encontraron modificaciones en la db: {diferencias}"
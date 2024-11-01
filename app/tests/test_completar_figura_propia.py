from factory import crear_partida, unir_jugadores, iniciar_partida, establecer_tablero, cartear_figuras, listas_to_casillas_figura, falsear_movimientos_parciales, eliminar_cartas_figura_del_maso
from verifications import check_response, check_cartas_figura_reveladas
from tools import capturar_metadata, comparar_capturas, get_all_tables
from websockets_manager.ws_partidas_manager import HAY_GANADOR, ACTUALIZAR_CARTAS_FIGURA, ACTUALIZAR_CARTAS_MOVIMIENTO

def test_usar_figura_propia(client, test_db, test_ws_messages):
    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_messages[ACTUALIZAR_CARTAS_FIGURA] = [{"partida_id": 1}]
    test_ws_messages[ACTUALIZAR_CARTAS_MOVIMIENTO] = [{"partida_id": 1}]
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

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }

    # Configuramos el escenario
    partida, jugador_del_turno = configurar_test_figuras(test_db, tablero_mock, cartas_figura_carteadas=["f1"], n_movimientos_a_consumir=3)

    # Capturamos la BDD antes de los cambios
    captura_inicial = capturar_metadata(get_all_tables(test_db))

    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Capturamos la BDD luego de los cambios
    captura_final = capturar_metadata(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # Comparamos que los conjuntos (PORQUE EL ORDEN DE LAS CAPTURAS NO ES DETERMINISTA) de objetos sean los correctos
    assert set(modificaciones) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."
    assert set(eliminadas) == set(
        [
            ("cartas_de_movimiento", 1),    # Cartas de movimiento falseadas
            ("cartas_de_movimiento", 2),
            ("cartas_de_movimiento", 3),
            ("movimientos_parciales", 1),   # Movimientos parciales asociados a las cartas falseadas/consumidas
            ("movimientos_parciales", 2),
            ("movimientos_parciales", 3),
            ("cartas_de_figura", 51),        # Carta de figura usada
        ]
    ), "Fallo: Se esperaba otro conjunto de objetos eliminados."
    assert set(creadas) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."

    # Chequeamos que se haya consumido la carta correctamente
    check_cartas_figura_reveladas(jugador_del_turno, expected_codigos_figura=[])

    # Chequeamos que la mano de movimientos del jugador se haya "aplicado"
    assert jugador_del_turno.mano_movimientos == [], f"Fallo: Se esperaba que se aplicaran todos los movimientos del jugador, pero le quedan {len(jugador_del_turno.mano_movimientos)}."

# ----------------------------------------------------------------

def test_usar_figura_propia_yganar(client, test_db, test_ws_messages):
    '''Test de jugador que completa una figura y gana la partida'''

    test_ws_messages[HAY_GANADOR] = [{'partida_id': 1, 'jugador_id': 1, 'nombre': 'Creador'}]
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

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }

    # Configuramos el escenario
    partida, jugador_del_turno = configurar_test_figuras(test_db, tablero_mock, cartas_figura_carteadas=["f1"], n_movimientos_a_consumir=3)

    eliminar_cartas_figura_del_maso(test_db, jugador_del_turno, 1)

    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    test_db.commit()
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Chequeamos que se haya eliminado todo de la db
    assert get_all_tables(test_db) == [], "Fallo: Se esperaba que la base de datos estuviera vacía."
    

# ----------------------------------------------------------------

def test_usar_figura_propia_varias_figuras(client, test_db, test_ws_counts):
    
    # Tablero que deseamos que se utilice
    tablero_mock = [
        [2, 2, 2, 4, 1, 1],
        [1, 2, 1, 2, 2, 2],
        [1, 2, 1, 4, 2, 1],
        [1, 1, 1, 4, 2, 1],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
    ]

    # Diccionario con las casillas de las figuras formadas en el tablero del mock
    figuras_formadas_en_mock = {
        "figuras_a_resaltar": {
            "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]]
        }
    }

    # Transformamos del formato de listas al esperado por el endpoint
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    
    # Configuramos el escenario
    partida, jugador_del_turno = configurar_test_figuras(test_db, tablero_mock, cartas_figura_carteadas=["f1"], n_movimientos_a_consumir=2)
    
    # Capturamos la BDD antes de los cambios
    captura_inicial = capturar_metadata(get_all_tables(test_db))
    
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)
    
    # Capturamos la BDD luego de los cambios
    captura_final = capturar_metadata(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # Comparamos que los conjuntos (PORQUE EL ORDEN DE LAS CAPTURAS NO ES DETERMINISTA) de objetos sean los correctos
    assert set(modificaciones) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."
    assert set(eliminadas) == set(
        [
            ("cartas_de_movimiento", 1),    # Cartas de movimiento falseadas
            ("cartas_de_movimiento", 2),
            ("movimientos_parciales", 1),   # Movimientos parciales asociados a las cartas falseadas/consumidas
            ("movimientos_parciales", 2),
            ("cartas_de_figura", 51),        # Carta de figura usada
        ]
    ), "Fallo: Se esperaba otro conjunto de objetos eliminados."
    assert set(creadas) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."

    # Chequeamos que se haya consumido la carta correctamente
    check_cartas_figura_reveladas(jugador_del_turno, expected_codigos_figura=[])

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_counts[ACTUALIZAR_CARTAS_FIGURA] = 1
    test_ws_counts[ACTUALIZAR_CARTAS_MOVIMIENTO] = 1

# ----------------------------------------------------------------

def test_usar_figura_propia_varias_cartas(client, test_db, test_ws_counts):
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
    
    casillas_figura = listas_to_casillas_figura(figuras_formadas_en_mock["figuras_a_resaltar"]["f1"])[0]
    request_body = {
        "figura": casillas_figura,
        "carta_fig": "f1"
    }
    
    partida, jugador_del_turno = configurar_test_figuras(test_db, tablero_mock, cartas_figura_carteadas=["f1", "f2", "f1"], n_movimientos_a_consumir=3)
    
    # Capturamos la BDD antes de los cambios
    captura_inicial = capturar_metadata(get_all_tables(test_db))
    
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    check_response(response, status_code_esperado=200, respuesta_esperada=None)

    # Capturamos la BDD luego de los cambios
    captura_final = capturar_metadata(get_all_tables(test_db))
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    # Comparamos que los conjuntos (PORQUE EL ORDEN DE LAS CAPTURAS NO ES DETERMINISTA) de objetos sean los correctos
    assert set(modificaciones) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."
    assert set(eliminadas) == set(
        [
            ("cartas_de_movimiento", 1),    # Cartas de movimiento falseadas
            ("cartas_de_movimiento", 2),
            ("cartas_de_movimiento", 3),
            ("movimientos_parciales", 1),   # Movimientos parciales asociados a las cartas falseadas/consumidas
            ("movimientos_parciales", 2),
            ("movimientos_parciales", 3),
            ("cartas_de_figura", 51),        # Carta de figura usada
        ]
    ), "Fallo: Se esperaba otro conjunto de objetos eliminados."
    assert set(creadas) == set(), "Fallo: Se esperaba otro conjunto de objetos modificados."

    # Chequeamos que se haya consumido una unica carta correctamente
    check_cartas_figura_reveladas(jugador_del_turno, expected_codigos_figura=["f2", "f1"])
    
    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws_counts[ACTUALIZAR_CARTAS_FIGURA] = 1
    test_ws_counts[ACTUALIZAR_CARTAS_MOVIMIENTO] = 1

# ----------------------------------------------------------------

def configurar_test_figuras(test_db, tablero_mock, cartas_figura_carteadas, n_movimientos_a_consumir):
    '''
    Configura un escenario medianamente general para los tests de completar figuras.
    
    A la salida de este procedimiento, la base de datos test_db queda con:
    - Una nueva partida iniciada
    - El jugador del turno tendrá en su mazo las cartas reveladas con los códigos de "cartas_figura_carteadas"
    - "n_movimientos_a_consumir" del jugador determina cuántas cartas de movimiento del jugador del turno estarán "parcialmente usadas"
    
    Retorna: 
    partida, jugador_del_turno
    '''
    
    
    # Creamos las bases de la partida
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)
    
    # Configuramos particularidades del jugador que posee el turno
    establecer_tablero(test_db, partida, tablero_mock)
    
    jugador_del_turno = partida.jugador_del_turno
    cartear_figuras(test_db, jugador_del_turno, cartas_figura_carteadas)
    
    movimientos_a_consumir = jugador_del_turno.mano_movimientos[0:n_movimientos_a_consumir]
    falsear_movimientos_parciales(test_db, partida, movimientos_a_consumir)

    return partida, jugador_del_turno

# ----------------------------------------------------------------

def test_usar_figura_propia_jugador_no_turno_403(client, test_db, test_ws_counts):
    '''Test de jugador que no es del turno intentando usar una figura propia'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=1)
    iniciar_partida(test_db, partida)

    jugador_del_turno = partida.jugador_del_turno
    otro_jugador = partida.jugadores[1]
    assert jugador_del_turno != otro_jugador, "Se cambio models y no se actualizo el test"
    
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
    response = client.put(f'/juego/{partida.id}/jugadores/{otro_jugador.id}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"El jugador con ID {otro_jugador.id} no posee el turno."}
    check_response(response, status_code_esperado=403, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura, *otro_jugador.mazo_cartas_de_figura])
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert not modificaciones, f"Se encontraron modificaciones en tablas en la db: {modificaciones}"
    assert not eliminadas, f"Se encontraron tablas eliminadas en la db: {eliminadas}"
    assert not creadas, f"Se encontraron tablas creadas en la db: {creadas}"
# ----------------------------------------------------------------

def test_usar_figura_propia_partida_no_existe_404(client, test_db, test_ws_counts):
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

def test_usar_figura_propia_partida_no_iniciada_403(client, test_db, test_ws_counts):
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
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador.id}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"La partida con ID {partida.id} todavía no comenzó."}
    check_response(response, status_code_esperado=403, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador.mazo_cartas_de_figura])
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert not modificaciones, f"Se encontraron modificaciones en tablas en la db: {modificaciones}"
    assert not eliminadas, f"Se encontraron tablas eliminadas en la db: {eliminadas}"
    assert not creadas, f"Se encontraron tablas creadas en la db: {creadas}"
# ----------------------------------------------------------------

def test_usar_figura_propia_jugador_no_existe_404(client, test_db, test_ws_counts):
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

def test_usar_figura_propia_mano_sin_figura_404(client, test_db, test_ws_counts):
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
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"El jugador no tiene en la mano ninguna carta de figura revelada del formato {request_body.get('carta_fig')}."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert not modificaciones, f"Se encontraron modificaciones en tablas en la db: {modificaciones}"
    assert not eliminadas, f"Se encontraron tablas eliminadas en la db: {eliminadas}"
    assert not creadas, f"Se encontraron tablas creadas en la db: {creadas}"
# ----------------------------------------------------------------

def test_usar_figura_propia_no_en_tablero_404(client, test_db, test_ws_counts):
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
    response = client.put(f'/juego/{partida.id}/jugadores/{jugador_del_turno.id}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"No existe (en el tablero) ninguna figura del tipo que se intenta utilizar."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert not modificaciones, f"Se encontraron modificaciones en tablas en la db: {modificaciones}"
    assert not eliminadas, f"Se encontraron tablas eliminadas en la db: {eliminadas}"
    assert not creadas, f"Se encontraron tablas creadas en la db: {creadas}"
# ----------------------------------------------------------------

def test_usar_figura_propia_casilla_incorrecta_404(client, test_db, test_ws_counts):
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
    response = client.put(f'/juego/{partida.id}/jugadores/{creador.id}/tablero/figura', json=request_body)
    respuesta_esperada = {'detail': f"No existe (en el tablero) la figura que se intenta utilizar en las coordenadas enviadas."}
    check_response(response, status_code_esperado=404, respuesta_esperada=respuesta_esperada)

    # Verificamos que no se haya realizado ningun cambio en la base de datos
    test_db.refresh(partida)
    captura_final = capturar_metadata([partida, *partida.jugadores, *jugador_del_turno.mazo_cartas_de_figura])
    modificaciones, eliminadas, creadas = comparar_capturas(captura_inicial, captura_final)

    assert not modificaciones, f"Se encontraron modificaciones en tablas en la db: {modificaciones}"
    assert not eliminadas, f"Se encontraron tablas eliminadas en la db: {eliminadas}"
    assert not creadas, f"Se encontraron tablas creadas en la db: {creadas}"

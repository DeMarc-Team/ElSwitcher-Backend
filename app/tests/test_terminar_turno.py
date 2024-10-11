from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida
from websockets_manager.ws_partidas_manager import ACTUALIZAR_TURNO

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
    test_db.commit()

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

    # Comprobamos que el turno sea del jugaddor correspondiente
    assert partida.jugador_del_turno.id_jugador == segundo_jugador.id_jugador
    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = 1

def test_vuelta_completa(test_db, test_ws):
    '''Test que chequea el funcionamiento de una vuelta completa de turnos.'''

    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

    id_jugador_inicial = partida.jugador_id
    id_jugador_anterior = None

    for i in range(0, len(partida.jugadores)):
        # Obtenemos el id del jugador actual
        id_jugador_actual = partida.jugador_id

        # Verificamos que efectivamente se haya cambiador el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."
        
        id_jugador_anterior = id_jugador_actual
        
        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
        test_db.commit()

    # Obtenemos el id del nuevo jugador actual
    id_jugador_final = partida.jugador_id
        
    # Verificamos que los turnos "hayan dado la vuelta completa"
    assert id_jugador_inicial == id_jugador_final, f"Fallo: Se esperaba que el último jugador fuera el mismo que el inicial, pero eso no ocurrió."
    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = len(partida.jugadores)

def test_varias_rondas(test_db, test_ws):
    '''Test sobre la confiabilidad de los turnos a lo largo de varias rondas.'''
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)

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
        test_db.commit()

    # Verificamos que se haya pasado por todos los jugadores
    assert len(set(orden_de_turnos)) == len(partida.jugadores)
    
    # Hacemos 4 rondas mas para ver si tal orden se mantiene
    for i in range(0, 4 * len(partida.jugadores)):

        # Obtenemos el id del jugador actual
        id_jugador_actual = partida.jugador_id

        # Verificamos que se este siguiendo el mismo orden de antes
        assert orden_de_turnos[i%len(partida.jugadores)] == id_jugador_actual
        id_jugador_anterior = id_jugador_actual

        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')
        test_db.commit()

    assert len(partida.jugadores) == 4, f"Fallo: Se esperaba que la cantidad de jugadores fuera la misma, pero no es así."

    # Ponemos cuantas veces se espera que se envie cada mensaje de ws
    test_ws[ACTUALIZAR_TURNO] = 5 * len(partida.jugadores)

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

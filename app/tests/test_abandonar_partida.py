import pytest

from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import SINCRONIZAR_TURNO, ACTUALIZAR_SALA_ESPERA, ACTUALIZAR_TURNO, HAY_GANADOR, PARTIDA_CANCELADA, ACTUALIZAR_TABLERO
from factory import crear_partida, unir_jugadores, iniciar_partida, siguiente_turno, test_temporizadores_turno, get_jugador_sin_turno
from verifications import check_jugador_abandoned, check_partida_deletion, check_response
from constantes_juego import SEGUNDOS_TEMPORIZADOR_TURNO
from tools import get_all_tables

@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_en_el_turno_200(client, test_db, test_ws_messages, numero_de_jugadores, mock_timeGmt):
    '''Test de jugador abandonando una partida en su turno'''

    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_TURNO] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}, {'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]

    # Inicializamos la precondicion
    partida, _ = crear_partida(db=test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores-1)
    jugador_del_turno = partida.jugador_del_turno
    id_jugador = jugador_del_turno.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(db=test_db, partida=partida)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [1, 2, 3, 4])
def test_abandonar_partida_no_iniciada_creador_200(client, test_db, test_ws_messages, numero_de_jugadores):
    '''Test de creador abandonando su partida no iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[PARTIDA_CANCELADA] = [{'partida_id': 1}]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    id_creador = creador.id_jugador
    id_partida = partida.id
    unir_jugadores(test_db, partida, numero_de_jugadores-1)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_partida_deletion(test_db, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [2, 3, 4])
def test_abandonar_partida_no_iniciada_no_creador_200(client, test_db, test_ws_counts, numero_de_jugadores):
    '''Test de jugador no creador abandonando una partida no iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_counts[ACTUALIZAR_SALA_ESPERA] = 1
    test_ws_counts[ACTUALIZAR_PARTIDAS] = 1
    test_ws_counts[ACTUALIZAR_TABLERO] = 1

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]
    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_iniciada_creador_200(client, test_db, test_ws_messages, numero_de_jugadores):
    '''Test de creador abandonando su partida iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)
    siguiente_turno(test_db, partida)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_creador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_iniciada_no_creador_200(client, test_db, test_ws_messages, numero_de_jugadores):
    '''Test de jugador no creador abandonando una partida iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]

    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------

def test_abandonar_partida_no_existente_404(client, test_db, test_ws_messages):
    '''Test de jugador abandonando una partida que no existe'''
    id_partida = 1
    id_jugador = 1

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    check_response(response, 404, respuesta_esperada)

# ----------------------------------------------------------------

def test_abandonar_partida_jugador_no_existente_404(client, test_db, test_ws_messages):
    '''Test de jugador no existente abandonando una partida'''
    partida, creador = crear_partida(test_db)
    id_partida = partida.id
    id_jugador = 2

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': f'Jugador con ID {id_jugador} no encontrado en la partida con ID {id_partida}.'}
    check_response(response, 404, respuesta_esperada)

# ----------------------------------------------------------------

def test_abandonar_partida_iniciada_ultimo_jugador_200(client, test_db, test_ws_messages):
    '''Test de jugador abandonando una partida iniciada y queda solo un jugador'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[HAY_GANADOR] = [{'partida_id': 1, 'jugador_id': 1, 'nombre': 'Creador'}]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    jugador = unir_jugadores(test_db, partida)[0]
    id_jugador = jugador.id_jugador
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_partida_deletion(test_db, id_partida)

# ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_integracion_abandonar_partida_iniciada_ultimo_jugador_200(client, test_db, test_ws_messages, mock_timeGmt):
    '''Test de jugador abandonando una partida iniciada y queda solo un jugador'''
    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    jugador = unir_jugadores(test_db, partida)[0]
    id_jugador = jugador.id_jugador
    id_creador = creador.id_jugador
    id_partida = partida.id
    
    # Iniciamos la partida a traves de la ruta
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]
    
    response = client.put(test_db, "partidas/1")
    check_response(response, 200, {'details': 'Partida iniciada correctamente', 'partida_id': 1})

    # await test_temporizadores_turno.wait_for_all_tasks()
    
    # Pasamos un turno a traves de la ruta
    test_ws_messages[ACTUALIZAR_TURNO] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO].extend([{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}])

    response = client.put(test_db, f'/juego/{partida.id}/jugadores/{partida.jugador_del_turno.id}/turno')
    check_response(response, 200, None)
    
    # await test_temporizadores_turno.wait_for_all_tasks()
    test_db.refresh(partida)
    
    # Hacemos que un jugador abandone la partida
    jugador_ganador = partida.jugador_del_turno
    test_ws_messages[HAY_GANADOR] = [{'partida_id': 1, 'jugador_id': jugador_ganador.id, 'nombre': jugador_ganador.nombre}]
    
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{get_jugador_sin_turno(test_db, partida).id}")
    check_response(response, 200, {'detail': 'El jugador abandonó la partida exitosamente'})

    # Verificamos que la base de datos se haya actualizado correctamente
    assert get_all_tables(test_db) == [], f"Fallo: Se esperaba que la base de datos estuviera vacia, pero se obtuvo {get_all_tables()}"

    await test_temporizadores_turno.wait_for_all_tasks()
    
    
@pytest.mark.parametrize("numero_de_jugadores", [2])
@pytest.mark.asyncio
async def test_abandonar_partida_en_el_turno_ultimo_jugador_200(client, test_db, test_ws_messages, numero_de_jugadores, mock_timeGmt):
    '''Test de jugador abandonando una partida en su turno, quedando solo un jugador (ganando)'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[HAY_GANADOR] = [{'partida_id': 1, 'jugador_id': 2, 'nombre': 'Jugador2'}]
    test_ws_messages[ACTUALIZAR_TURNO] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]

    # Inicializamos la precondicion
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida,numero_de_jugadores-1)
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{partida.jugador_del_turno.id}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    assert get_all_tables(test_db) == [], f"Fallo: Se esperaba que la base de datos estuviera vacia, pero se obtuvo {get_all_tables()}"
    
    await test_temporizadores_turno.wait_for_all_tasks()
    

@pytest.mark.parametrize("numero_de_jugadores", [2])
@pytest.mark.asyncio
async def test_integracion_abandonar_partida_en_el_turno_ultimo_jugador_200(client, test_db, test_ws_messages, numero_de_jugadores, mock_timeGmt):
    '''Test de jugador abandonando una partida en su turno, quedando solo un jugador (ganando)'''
    # Inicializamos la precondicion
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida,numero_de_jugadores-1)
    id_partida = partida.id
    
    # Iniciamos la partida a traves de la ruta
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO] = [{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}]
    
    response = client.put(test_db, "partidas/1")
    check_response(response, 200, {'details': 'Partida iniciada correctamente', 'partida_id': 1})
    test_db.refresh(partida)
    
    # Abandonamos al jugador del turno
    ganador = get_jugador_sin_turno(test_db, partida)
    test_ws_messages[HAY_GANADOR] = [{'partida_id': 1, 'jugador_id': ganador.id, 'nombre': ganador.nombre}]
    test_ws_messages[ACTUALIZAR_TURNO] = [{'partida_id': 1}]
    test_ws_messages[ACTUALIZAR_TABLERO] = [{'partida_id': 1}]
    test_ws_messages[SINCRONIZAR_TURNO].extend([{'partida_id': 1, 'inicio': mock_timeGmt, 'duracion': SEGUNDOS_TEMPORIZADOR_TURNO}])
    

    response = client.delete(test_db, f"/partidas/{id_partida}/jugadores/{partida.jugador_del_turno.id}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    assert get_all_tables(test_db) == [], f"Fallo: Se esperaba que la base de datos estuviera vacia, pero se obtuvo {get_all_tables()}"
    
    await test_temporizadores_turno.wait_for_all_tasks()
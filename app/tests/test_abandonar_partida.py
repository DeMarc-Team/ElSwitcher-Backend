import pytest

from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import ACTUALIZAR_SALA_ESPERA, ACTUALIZAR_TURNO, HAY_GANADOR, PARTIDA_CANCELADA, ACTUALIZAR_TABLERO
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida
from verifications import check_jugador_abandoned, check_partida_deletion, check_response


@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_en_el_turno_200(test_db, test_ws, numero_de_jugadores):
    '''Test de jugador abandonando una partida en su turno'''

    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws[ACTUALIZAR_SALA_ESPERA] = 1
    test_ws[ACTUALIZAR_TURNO] = 1
    test_ws[ACTUALIZAR_PARTIDAS] = 1
    test_ws[ACTUALIZAR_TABLERO] = 1

    # Inicializamos la precondicion
    partida, _ = crear_partida(db=test_db)
    unir_jugadores(test_db, partida, numero_de_jugadores-1)
    jugador_del_turno = partida.jugador_del_turno
    id_jugador = jugador_del_turno.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(db=test_db, partida=partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [1, 2, 3, 4])
def test_abandonar_partida_no_iniciada_creador_200(test_db, test_ws, numero_de_jugadores):
    '''Test de creador abandonando su partida no iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws[ACTUALIZAR_PARTIDAS] = 1
    test_ws[PARTIDA_CANCELADA] = 1

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    id_creador = creador.id_jugador
    id_partida = partida.id
    unir_jugadores(test_db, partida, numero_de_jugadores-1)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_partida_deletion(test_db, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [2, 3, 4])
def test_abandonar_partida_no_iniciada_no_creador_200(test_db, test_ws, numero_de_jugadores):
    '''Test de jugador no creador abandonando una partida no iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws[ACTUALIZAR_SALA_ESPERA] = 1
    test_ws[ACTUALIZAR_TURNO] = 1
    test_ws[ACTUALIZAR_PARTIDAS] = 1
    test_ws[ACTUALIZAR_TABLERO] = 1

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]
    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_iniciada_creador_200(test_db, test_ws, numero_de_jugadores):
    '''Test de creador abandonando su partida iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws[ACTUALIZAR_SALA_ESPERA] = 1
    test_ws[ACTUALIZAR_TURNO] = 1
    test_ws[ACTUALIZAR_PARTIDAS] = 1
    test_ws[ACTUALIZAR_TABLERO] = 1

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_creador, id_partida)

# ----------------------------------------------------------------


@pytest.mark.parametrize("numero_de_jugadores", [3, 4])
def test_abandonar_partida_iniciada_no_creador_200(test_db, test_ws_messages, numero_de_jugadores):
    '''Test de jugador no creador abandonando una partida iniciada'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [(1,)]
    test_ws_messages[ACTUALIZAR_TURNO] = [(1,)]
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [()]
    test_ws_messages[ACTUALIZAR_TABLERO] = [(1,)]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, numero_de_jugadores-1)[0]

    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_jugador_abandoned(test_db, numero_de_jugadores-1, id_jugador, id_partida)

# ----------------------------------------------------------------


def test_abandonar_partida_no_existente_404(test_db, test_ws_messages):
    '''Test de jugador abandonando una partida que no existe'''
    id_partida = 1
    id_jugador = 1

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    check_response(response, 404, respuesta_esperada)

# ----------------------------------------------------------------


def test_abandonar_partida_jugador_no_existente_404(test_db, test_ws_messages):
    '''Test de jugador no existente abandonando una partida'''
    partida, creador = crear_partida(test_db)
    id_partida = partida.id
    id_jugador = 2

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {'detail': f'Jugador con ID {id_jugador} no encontrado en la partida con ID {id_partida}.'}
    check_response(response, 404, respuesta_esperada)

# ----------------------------------------------------------------


def test_abandonar_partida_iniciada_ultimo_jugador_200(test_db, test_ws_messages):
    '''Test de jugador abandonando una partida iniciada y queda solo un jugador'''
    # Ponemos cuantas veces se espera que se envie cada ws
    test_ws_messages[HAY_GANADOR] = [(1, 1, 'Creador')]

    # Inicializamos la precondicion
    partida, creador = crear_partida(test_db)
    jugador = unir_jugadores(test_db, partida)[0]
    id_jugador = jugador.id_jugador
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    respuesta_esperada = {
        'detail': 'El jugador abandonó la partida exitosamente'}
    check_response(response, 200, respuesta_esperada)

    # Verificamos que la base de datos se haya actualizado correctamente
    check_partida_deletion(test_db, id_partida)

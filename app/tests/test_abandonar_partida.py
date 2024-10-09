from unittest.mock import patch
from tests_setup import client
from factory import crear_partida, unir_jugadores, iniciar_partida
from models import Partida, Jugador

def test_abandonar_partida_en_el_turno_200(test_db):
    '''Test de jugador abandonando una partida en su turno'''
    partida, _ = crear_partida(db=test_db)
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)
    jugador_del_turno = partida.jugador_del_turno
    id_jugador = jugador_del_turno.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(db=test_db, partida=partida)
    
    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

    # Verificamos que la base de datos se haya actualizado correctamente
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()

    assert len(partida.jugadores) == 2, f"Fallo: Se esperaban 2 jugadores en la partida, pero se obtuvo {len(partida.jugadores)}"
    assert jugador_del_turno not in partida.jugadores, f"Fallo: Se esperaba que el jugador abandonara la partida, pero no se encontró en la lista de jugadores"
    assert partida.jugador_del_turno.id_jugador != id_jugador, f"Fallo: Se esperaba que el jugador del turno no fuera el jugador que abandonó, pero se obtuvo {partida.jugador_del_turno.id_jugador}"

    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    assert jugador == None, f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

# ----------------------------------------------------------------

def test_abandonar_partida_no_iniciada_creador_403(test_db):
    '''Test de creador abandonando su partida no iniciada (no deberia poder)'''
    partida, creador = crear_partida(test_db)
    id_creador = creador.id_jugador
    id_partida = partida.id

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {"detail": f"El creador con ID {id_creador} no puede abandonar la partida con ID {id_partida} antes de iniciarla."}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_abandonar_partida_no_iniciada_no_creador_200(test_db):
    '''Test de jugador no creador abandonando una partida no iniciada'''
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, 2)[0]
    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

    # Verificamos que la base de datos se haya actualizado correctamente
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()
    assert len(partida.jugadores) == 2, f"Fallo: Se esperaba 2 jugadores en la partida, pero se obtuvo {len(partida.jugadores)}"
    assert nuevo_jugador not in partida.jugadores, f"Fallo: Se esperaba que el jugador abandonara la partida, pero no se encontró en la lista de jugadores"

    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    assert jugador == None, f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

# ----------------------------------------------------------------

def test_abandonar_partida_iniciada_creador_200(test_db):
    '''Test de creador abandonando su partida iniciada'''
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida,2)[0]
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_creador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

    # Verificamos que la base de datos se haya actualizado correctamente
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()
    assert partida != None, f"Fallo: Se esperaba que la partida no fuera eliminada de la base de datos, pero no se encontró {partida}"
    assert len(partida.jugadores) == 2, f"Fallo: Se esperaba 2 jugadores en la partida, pero se obtuvo {len(partida.jugadores)}"
    assert creador not in partida.jugadores, f"Fallo: Se esperaba que el creador abandonara la partida, pero no se encontró en la lista de jugadores"

    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_creador).first()
    assert jugador == None, f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

# ----------------------------------------------------------------

def test_abandonar_partida_iniciada_no_creador_200(test_db):
    '''Test de jugador no creador abandonando una partida iniciada'''
    partida, creador = crear_partida(test_db)
    nuevo_jugador = unir_jugadores(test_db, partida, 2)[0]
    
    id_jugador = nuevo_jugador.id_jugador
    id_partida = partida.id

    partida = iniciar_partida(test_db, partida)

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

    # Verificamos que la base de datos se haya actualizado correctamente
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()
    assert len(partida.jugadores) == 2, f"Fallo: Se esperaba 2 jugadores en la partida, pero se obtuvo {len(partida.jugadores)}"
    assert nuevo_jugador not in partida.jugadores, f"Fallo: Se esperaba que el jugador abandonara la partida, pero no se encontró en la lista de jugadores"

    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    assert jugador == None, f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

# ----------------------------------------------------------------

def test_abandonar_partida_no_existente_404(test_db):
    '''Test de jugador abandonando una partida que no existe'''
    id_partida = 1
    id_jugador = 1

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_abandonar_partida_jugador_no_existente_404(test_db):
    '''Test de jugador no existente abandonando una partida'''
    partida, creador = crear_partida(test_db)
    id_partida = partida.id
    id_jugador = 2

    # Realizamos la petición
    response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': f'Jugador con ID {id_jugador} no encontrado en la partida con ID {id_partida}.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_abandonar_partida_iniciada_ultimo_jugador_200(test_db):
    '''Test de jugador abandonando una partida iniciada donde es el último jugador'''
    partida, creador = crear_partida(test_db)
    jugador = unir_jugadores(test_db, partida)[0]
    id_jugador = jugador.id_jugador
    id_creador = creador.id_jugador
    id_partida = partida.id
    partida = iniciar_partida(test_db, partida)

    ganador_id = id_creador
    ganador_nombre = creador.nombre

    ws_home_manager_path = 'websockets_manager.ws_home_manager.ws_home_manager'
    ws_partidas_manager_path = 'websockets_manager.ws_partidas_manager.ws_partidas_manager'
    # Mockeamos los WebSockets
    with patch(f'{ws_home_manager_path}.send_actualizar_partidas') as mock_actualizar_partidas, \
         patch(f'{ws_partidas_manager_path}.send_actualizar_sala_espera') as mock_actualizar_sala_espera, \
         patch(f'{ws_partidas_manager_path}.send_actualizar_turno') as mock_actualizar_turno, \
         patch(f'{ws_partidas_manager_path}.send_ganador') as mock_send_ganador:

        # Realizamos la petición
        response = client.delete(f"/partidas/{id_partida}/jugadores/{id_jugador}")
        print(f"Response: {response.json()}")

        # Verificamos que la respuesta sea la esperada
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        respuesta_esperada = {'detail': 'El jugador abandonó la partida exitosamente'}
        assert response.json() == respuesta_esperada, f"Fallo: Se esperaba '{respuesta_esperada}', pero se obtuvo {response.json()}"

        # Verificamos que los WebSockets se enviaron
        mock_actualizar_partidas.assert_called_once()
        mock_actualizar_sala_espera.assert_called_once_with(id_partida)
        mock_actualizar_turno.assert_called_once_with(id_partida)

        if ganador_id is not None:
            mock_send_ganador.assert_called_once_with(id_partida, ganador_id, ganador_nombre)
    # Verificamos que la base de datos se haya actualizado correctamente
    partida = test_db.query(Partida).filter(Partida.id == id_partida).first()
    assert partida == None, f"Fallo: Se esperaba que la partida fuera eliminada de la base de datos, pero se encontró {partida}"

    jugador = test_db.query(Jugador).filter(Jugador.id_jugador == id_jugador).first()
    assert jugador == None, f"Fallo: Se esperaba que el jugador fuera eliminado de la base de datos, pero se encontró {jugador}"

    creador = test_db.query(Jugador).filter(Jugador.id_jugador == id_creador).first()
    assert creador == None, f"Fallo: Se esperaba que el creador fuera eliminado de la base de datos, pero se encontró {creador}"


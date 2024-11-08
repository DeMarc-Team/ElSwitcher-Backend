from models import Jugador, Partida
from factory import crear_partida, crear_partida_privada, unir_jugadores, iniciar_partida
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS
from websockets_manager.ws_partidas_manager import ACTUALIZAR_SALA_ESPERA, ACTUALIZAR_TURNO, HAY_GANADOR, PARTIDA_CANCELADA, ACTUALIZAR_TABLERO

def test_unirse_partida_200(client, test_db, test_ws_messages):
    '''Test al unirse a una partida existente no llena'''
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    test_ws_messages[ACTUALIZAR_SALA_ESPERA] = [{'partida_id': 1}]
    
    # Creamos una partida con 2 jugadores
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_para_unirse", nombre_creador="Creador1")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)

    # Enviamos la solicitud al servidor
    body = {"nombre": "Jugador4"}
    response = client.post(test_db, "partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'nombre': 'Jugador4', 'id_jugador': 4}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que se haya actualizado la db
    jugadores = test_db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 4, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    test_db.close()

# ----------------------------------------------------------------

def test_unirse_partida_llena_403(client, test_db):
    '''Test al unirse a una partida llena'''
    # Creamos una partida con 4 jugadores
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_llena", nombre_creador="Creador2")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=3)

    # Enviamos la solicitud al servidor
    body = {"nombre": "Jugador5"}
    response = client.post(test_db, "partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")

    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada ={'detail': 'Partida con ID 1 está llena. Máximo de jugadores: 4.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que no se haya actualizado la db
    jugadores = test_db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 4, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    test_db.close()

# ----------------------------------------------------------------

def test_unirse_partida_iniciada_403(client, test_db):
    '''Test al unirse a una partida ya iniciada'''
    # Creamos una partida con 2 jugadores y la iniciamos
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_iniciada", nombre_creador="Creador3")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)
    iniciar_partida(db=test_db, partida=partida)

    # Enviamos la solicitud al servidor
    body = {"nombre": "Jugador5"}
    response = client.post(test_db, "partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'La partida con ID 1 ya está iniciada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
    
    # Verificamos que no se haya actualizado la db
    jugadores = test_db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 2, f"Fallo: Se esperaban 2 jugadores, pero se obtuvieron {len(jugadores)}"
    test_db.close()

# ----------------------------------------------------------------

def test_unirse_partida_404(client, test_db):
    '''Test al unirse a una partida inexistente'''
    body = {"nombre": "Jugador5"}
    response = client.post(test_db, "partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'No hay ningun elemento con ID 1 en la tabla partidas.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que no se haya actualizado la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert partida is None, f"Fallo: Se esperaba None, pero se obtuvo {partida}"

    jugador = test_db.query(Jugador).filter(Jugador.nombre == "Jugador5" ).first()
    assert jugador is None, f"Fallo: Se esperaba None, pero se obtuvo {jugador}"
    test_db.close()

# ----------------------------------------------------------------
def test_unirse_partida_privada(client,test_db):
    partida, creador = crear_partida_privada(test_db, nombre_partida="la gran partida", nombre_creador="el creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)
    body = {"nombre": "LEROOOOOOOOOY JENKIIIIIIIIIIIIIIIINSSSSSS",
            "contraseña": "ZXN0ZV9lc191bl9lYXN0ZXJfZWdnCg=="}
    response = client.post(test_db, "partidas/1/jugadores", json=body)

    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    # Verificamos que se haya actualizado la db
    jugadores = test_db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 4, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    test_db.close()

# ----------------------------------------------------------------
def test_unirse_partida_privada_mala_contraseña(client,test_db):
    partida, creador = crear_partida_privada(test_db, nombre_partida="la gran partida", nombre_creador="el creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)
    body = {"nombre": "LEROOOOOOOOOY",
            "contraseña": "JENKIIIIIIIIIIIIIIIINSSSSSS"}
    response = client.post(test_db, "partidas/1/jugadores", json=body)

    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'La contraseña provista es incorrecta'}
    assert response.json() == respuesta_esperada

    # Verificamos que no se haya actualizado la db
    jugadores = test_db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 3, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    test_db.close()

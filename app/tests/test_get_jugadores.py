from factory import crear_partida, unir_jugadores

def test_get_jugadores_200(client, test_db):
    '''Test para obtener los jugadores de una partida existente.'''
    partida, _ = crear_partida(db=test_db,nombre_partida="nombre_partida", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)
    
    # Llamamos al endpoint para obtener jugadores de la partida con ID 1 (existente)
    response = client.get(f"partidas/1/jugadores")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 3, f"Fallo: Se esperaban 3 jugadores, pero se obtuvieron {len(response.json())}"
    respuesta_esperada = [{'nombre': 'Creador', 'id_jugador': 1},
                          {'nombre': 'Jugador2', 'id_jugador': 2},
                          {'nombre': 'Jugador3', 'id_jugador': 3}]
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_get_jugadores_404(client, test_db):
    '''Test para obtener los jugadores de una partida que no existe.'''
    id_partida = 1
    response = client.get(f"partidas/{id_partida}/jugadores")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
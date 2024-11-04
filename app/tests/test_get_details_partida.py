from factory import crear_partida, unir_jugadores, iniciar_partida, abandonar_partida

def test_get_details_partida_sin_creador_200(client, test_db):
    '''
    Elimina al creador de una partida iniciada y prueba que
    se pueda obtener los detalles de la partida y sean correctos.
    '''
    partida, creador = crear_partida(test_db)
    unir_jugadores(test_db, partida, 2)
    iniciar_partida(test_db, partida)
    abandonar_partida(test_db, partida, creador)
   
    response = client.get(test_db, f"partidas/{partida.id}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'nombre_partida': 'Partida',
                          'nombre_creador': 'Creador',
                          'id': 1, 'id_creador': None,
                          'iniciada': True,
                          'espacios_disponibles': 2}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_get_details_partida_200(client, test_db):
    partida, _ = crear_partida(db=test_db,nombre_partida="partida_details", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    response = client.get(test_db, "partidas/1") 
    print(f"Response: {response.json()}")


    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'nombre_partida': 'partida_details',
                          'nombre_creador': 'Creador',
                          'id': 1,
                          'id_creador': 1,
                          'iniciada': False,
                          'espacios_disponibles': 2}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_get_details_partida_404(client, test_db):
    id_partida = 1
    response = client.get(test_db, f"partidas/{id_partida}") 
    print(f"Response: {response.json()}")
    
    
    assert response.status_code == 404 , f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': f'Partida con ID {id_partida} no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
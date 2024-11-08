from factory import crear_partida, unir_jugadores, iniciar_partida
import pytest

@pytest.mark.parametrize("numero_jugadores", [1, 2, 3])
def test_get_partidas_200(client, test_db, test_ws_counts, numero_jugadores):
    '''Test para obtener las partidas no iniciadas y no llenas'''
    # Creamos 3 partidas: una no iniciada, una iniciada y una llena
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_no_iniciada", nombre_creador="Creador1")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=numero_jugadores-1)

    partida, _ = crear_partida(db=test_db, nombre_partida="partida_iniciada", nombre_creador="Creador2")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)
    iniciar_partida(db=test_db, partida=partida)

    partida, _ = crear_partida(db=test_db, nombre_partida="partida_llena", nombre_creador="Creador3")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=3)

    # Llamamos al endpoint para obtener las partidas no iniciadas y no llenas
    response = client.get(test_db, "partidas")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = [{'nombre_partida': 'partida_no_iniciada',
                           'nombre_creador': 'Creador1',
                           'id': 1,
                           'id_creador': 1,
                           'iniciada': False,
                           'privada': False,
                           'numero_de_jugadores': numero_jugadores}]
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
from models import Partida, Jugador
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS

def test_create_partida(client, test_db, test_ws_messages):
    '''Test para crear una partida'''
    test_ws_messages[ACTUALIZAR_PARTIDAS] = [{}]
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post(test_db, "/partidas", json=nueva_partida)
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {  'nombre_partida': 'Partida_nueva',
                            'nombre_creador': 'Jugador_nuevo',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    respuesta_esperada = {  'nombre_partida': 'Partida_nueva',
                            'nombre_creador': 'Jugador_nuevo',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que la partida se haya creado correctamente en la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    print(partida)
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    assert partida.iniciada == False, f"Fallo: Se esperaba False como estado de la partida, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 1, f"Fallo: Se esperaba 1 jugador en la partida, pero se obtuvo {len(partida.jugadores)}"
    
    creador = test_db.query(Jugador).filter(Jugador.id_jugador == 1).first()
    print(creador)

    assert creador.nombre == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador, pero se obtuvo {creador.nombre}"
    assert creador.es_creador == True, f"Fallo: Se esperaba True como es_creador del creador, pero se obtuvo {creador.es_creador}"
    assert creador.partidas == partida, f"Fallo: Se esperaba la partida creada como partida del creador, pero se obtuvo {creador.partidas}"
    assert creador.orden == 0, f"Fallo: Se esperaba 0 como orden del creador, pero se obtuvo {creador.orden}"

    test_db.close()

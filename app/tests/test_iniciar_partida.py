from tests_setup import client
from models import Partida
from factory import crear_partida, unir_jugadores, iniciar_partida

def test_iniciar_partida_200(test_db):
    '''Test para iniciar una partida con suficientes jugadores'''
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)

    response = client.put("partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {
        response.status_code}"
    respuesta_esperada = {'details': 'Partida iniciada correctamemte', 'partida_id': 1}

    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json}"
    
    # Verificamos que se haya iniciado la partida
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert partida.iniciada, f"Fallo: Se esperaba que la partida estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 3, f"Fallo: Se esperaba que la partida tuviera 3 jugadores, pero se obtuvo {len(partida.jugadores)}"
    
    # Verificamos que se hayan repartido las cartas de figura y cartas de movimiento
    for jugador in partida.jugadores:
        assert len(jugador.mazo_cartas_de_figura) == 3, f"Fallo: Se esperaba que el jugador tuviera 3 cartas de figura, pero se obtuvo {len(jugador.mazo_cartas_de_figura)}"
        for carta in jugador.mazo_cartas_de_figura:
            assert carta.revelada, f"Fallo: Se esperaba que la carta de figura estuviera revelada, pero se obtuvo {carta.revelada}"
        assert len(jugador.mano_movimientos) == 3, f"Fallo: Se esperaba que el jugador tuviera 3 cartas de movimiento, pero se obtuvo {len(jugador.cartas_movimiento)}"
    
    test_db.close()

# ----------------------------------------------------------------

def test_iniciar_partida_con_jugadores_insuficientes_403(test_db):
    '''Test para iniciar una partida sin suficientes jugadores'''
    id_partida = 1
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_con_1_jugador", nombre_creador="Creador")

    response = client.put("partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {
        response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 1 no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"
    
    # Verificamos la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert not partida.iniciada, f"Fallo: Se esperaba que la partida no estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 1, f"Fallo: Se esperaba que la partida tuviera 1 jugador, pero se obtuvo {len(partida.jugadores)}"
    assert partida.jugadores[0].es_creador, f"Fallo: Se esperaba que el jugador fuera el creador, pero se obtuvo {partida.jugadores[0].es_creador}"
    assert partida.jugadores[0].mano_movimientos == [], f"Fallo: Se esperaba que el jugador no tuviera cartas de movimiento, pero se obtuvo {partida.jugadores[0].mano_movimientos}"
    assert partida.jugadores[0].mazo_cartas_de_figura == [], f"Fallo: Se esperaba que el jugador no tuviera cartas de figura, pero se obtuvo {partida.jugadores[0].mazo_cartas_de_figura}"
    test_db.close()

# ----------------------------------------------------------------

def test_iniciar_partida_ya_iniciada_403(test_db):
    '''Test para iniciar una partida que ya esta iniciada'''
    partida, _ = crear_partida(db=test_db, nombre_partida="partida_ya_iniciada", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)
    iniciar_partida(db=test_db, partida=partida)
    
    # 
    response = client.put("partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'La partida con ID 1 ya está iniciada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"
    
    # Verificamos la db
    partida = test_db.query(Partida).filter(Partida.id == 1).first()
    assert partida.iniciada, f"Fallo: Se esperaba que la partida estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 2, f"Fallo: Se esperaba que la partida tuviera 2 jugadores, pero se obtuvo {len(partida.jugadores)}"
    test_db.close()

# ----------------------------------------------------------------

def test_iniciar_partida_404(test_db):
    '''Test para iniciar una partida que no existe'''
    response = client.put("partidas/1")
    print(f"Response: {response.json()}")
    
    # Verificamos la respuesta del servidor
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {
        response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 1 no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada}, pero se obtuvo {response.json()}"
from tests_setup import client, TestingSessionLocal
from models import Jugador, Partida, Juego

import pytest


@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()

    partida1 = Partida(
        nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    creador1 = Jugador(nombre="Creador", partida_id=1,
                       es_creador=True, partidas=partida1)
    jugador1 = Jugador(nombre="Jugador1", partida_id=1, partidas=partida1)
    jugador2 = Jugador(nombre="Jugador2", partida_id=1, partidas=partida1)
    partida2 = Partida(nombre_partida="partida_con_1_jugador",
                       nombre_creador="Creador")
    creador2 = Jugador(nombre="Creador", partida_id=2,
                       es_creador=True, partidas=partida2)
    
    partida3 = Partida(nombre_partida="partida_ya_iniciada", nombre_creador="Creador", iniciada=True)
    juego3 = Juego(partida_id=3, partida=partida3)
    creador3 = Jugador(nombre="Creador", partida_id=3, es_creador=True, partidas=partida3)
    jugador3 = Jugador(nombre="Jugador1", partida_id=3, partidas=partida3)

    db.add(partida1)
    db.add(creador1)
    db.add(jugador1)
    db.add(jugador2)
    db.add(partida2)
    db.add(creador2)
    db.add(partida3)
    db.add(juego3)
    db.add(creador3)
    db.add(jugador3)

    db.commit()
    db.flush()
    db.close()
    yield db

    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.query(Juego).delete()
    db.commit()
    db.flush()
    db.close()


def test_iniciar_partida_200(test_data):
    '''Test para iniciar una partida con suficientes jugadores'''
    response = client.put("partidas/1")
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {
        response.status_code}"
    assert response.json() == {"message": "Partida iniciada correctamemte", "partida_id": 1}, f"Fallo: Se esperaba {
        {'message': 'Partida iniciada correctamemte', 'partida_id': 1}}, pero se obtuvo {response.json}"
    # Verificamos que se haya iniciado la partida
    db = test_data
    partida = db.query(Partida).filter(Partida.id == 1).first()
    assert partida.iniciada, f"Fallo: Se esperaba que la partida estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert partida.juego, f"Fallo: Se esperaba que la partida tuviera juego, pero se obtuvo {partida.juego}"
    db.close()


def test_iniciar_partida_con_jugadores_insuficientes_403(test_data):
    '''Test para iniciar una partida sin suficientes jugadores'''
    response = client.put("partidas/2")
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {
        response.status_code}"
    assert response.json()['detail'] == "Partida con ID 2 no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.", f"Fallo: Se esperaba 'Partida con ID 2 no tiene suficientes jugadores para iniciar. Mínimo de jugadores: 4.', pero se obtuvo {
        response.json()['detail']}"
    # Verificamos que no se haya iniciado la partida
    db = test_data
    partida = db.query(Partida).filter(Partida.id == 2).first()
    assert not partida.iniciada, f"Fallo: Se esperaba que la partida no estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert not partida.juego, f"Fallo: Se esperaba que la partida no tuviera juego, pero se obtuvo {partida.juego}"
    db.close()

def test_iniciar_partida_ya_iniciada_403(test_data):
    '''Test para iniciar una partida que ya esta iniciada'''
    response = client.put("partidas/3")
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {
        response.status_code}"
    assert response.json()['detail'] == "La partida con ID 3 ya está iniciada.", f"Fallo: Se esperaba 'La partida con ID 3 ya está iniciada.', pero se obtuvo {
        response.json()['detail']}"
    # Verificamos que no se haya iniciado la partida
    db = test_data
    partida = db.query(Partida).filter(Partida.id == 3).first()
    assert partida.iniciada, f"Fallo: Se esperaba que la partida estuviera iniciada, pero se obtuvo {partida.iniciada}"
    assert partida.juego, f"Fallo: Se esperaba que la partida tuviera juego, pero se obtuvo {partida.juego}"
    db.close()

def test_iniciar_partida_404(test_data):
    '''Test para iniciar una partida que no existe'''
    response = client.put("partidas/4")
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {
        response.status_code}"
    assert response.json()['detail'] == "Partida con ID 4 no encontrada.", f"Fallo: Se esperaba 'Partida con ID 4 no encontrada.', pero se obtuvo {
        response.json()['detail']}"
from tests_setup import client, TestingSessionLocal
from models import Partida
from models import Jugador
import pytest

# Decorador "fixture" para preparar el entorno de prueba. 
@pytest.fixture(scope="function")
def test_data():
    # Cargamos en la db de prueba una partida con dos jugadores
    db = TestingSessionLocal()

    partida1 = Partida(nombre_partida="partida_no_iniciada", nombre_creador="Jugador1", iniciada=False)
    jugador1 = Jugador(nombre="Jugador1", partida_id=1, es_creador=True)
    jugador2 = Jugador(nombre="Jugador2", partida_id=1)
    partida2 = Partida(nombre_partida="partida_iniciada", nombre_creador="Jugador1", iniciada=True)
    partida3 = Partida(nombre_partida="partida_llena", nombre_creador="Jugador1", iniciada=False)
    jugador3 = Jugador(nombre="Jugador3", partida_id=3)
    jugador4 = Jugador(nombre="Jugador4", partida_id=3)
    jugador5 = Jugador(nombre="Jugador5", partida_id=3)
    jugador6 = Jugador(nombre="Jugador6", partida_id=3)
    db.add(partida1)
    db.add(jugador1)
    db.add(jugador2)
    db.add(partida2)
    db.add(partida3)
    db.add(jugador3)
    db.add(jugador4)
    db.add(jugador5)
    db.add(jugador6)

    db.commit()

    yield  db
    db.close()


def test_get_partidas_200(test_data):
    '''Test para obtener las partidas no iniciadas y no llenas'''
    response = client.get("partidas")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = [{'nombre_partida': 'partida_no_iniciada',
                           'nombre_creador': 'Jugador1',
                           'id': 1,
                           'id_creador': 1,
                           'iniciada': False}]
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
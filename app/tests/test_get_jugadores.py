from tests_setup import client, TestingSessionLocal
from models import Jugador
from models import Partida

import pytest

# Decorador "fixture" para preparar el entorno de prueba. 
@pytest.fixture(scope="function")
def test_data():
    # Cargamos en la db de prueba una partida con dos jugadores
    db = TestingSessionLocal()

    partida = Partida(nombre_partida="nombre_partida", nombre_creador="Jugador1", iniciada=False)
    jugador1 = Jugador(nombre="Jugador1", partida_id=1)
    jugador2 = Jugador(nombre="Jugador2", partida_id=1)

    db.add(partida)
    db.add(jugador1)
    db.add(jugador2)

    db.commit()
    db.flush()
    db.close()

    # Cerramos la sesión antes de salir del fixture
    yield  # Este es el punto donde se ejecutan las pruebas

    # Limpiamos la base de datos después de la prueba
    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.commit()
    db.close()


def test_get_jugadores_partida_existente(test_data):
    # Llamamos al endpoint para obtener jugadores de la partida con ID 1 (existente)
    response = client.get("partidas/1/jugadores")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['nombre'] == "Jugador1"
    assert response.json()[1]['nombre'] == "Jugador2"
    #Test exitoso: Se obtuvieron los jugadores de una partida existente

def test_get_jugadores_partida_inexistente():
    # Llamamos al endpoint para obtener jugadores de la partida con ID 2 (inexistente)
    response = client.get("partidas/2/jugadores")
    print(f"Response: {response.json()}")
    assert response.status_code == 404
    assert len(response.json()) == 1
    #Test exitoso: Se devolvio 404 not found a la peticion de los jugadores de una partida inexistente

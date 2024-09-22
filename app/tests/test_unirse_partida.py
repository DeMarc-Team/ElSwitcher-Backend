from tests_setup import client, TestingSessionLocal
from models.jugadores import Jugador
from models.partidas import Partida

import pytest


@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()

    partida1 = Partida(nombre_partida="nombre_partida",
                       nombre_creador="Creador1", iniciada=False)
    jugador11 = Jugador(nombre="Creador1", partida_id=1)
    jugador12 = Jugador(nombre="Jugador2", partida_id=1)
    jugador13 = Jugador(nombre="Jugador3", partida_id=1)

    db.add(partida1)
    db.add(jugador11)
    db.add(jugador12)
    db.add(jugador13)

    partida2 = Partida(nombre_partida="partida_llena",
                       nombre_creador="Creador2", iniciada=False)
    jugador21 = Jugador(nombre="Creador2", partida_id=2)
    jugador22 = Jugador(nombre="Jugador2", partida_id=2)
    jugador23 = Jugador(nombre="Jugador3", partida_id=2)
    jugador24 = Jugador(nombre="Jugador4", partida_id=2)

    db.add(partida2)
    db.add(jugador21)
    db.add(jugador22)
    db.add(jugador23)
    db.add(jugador24)

    db.commit()
    db.flush()
    db.close()

    yield

    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.commit()
    db.close()


def test_post_200(test_data):
    body = {"nombre": "Jugador4"}
    response = client.post("partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()['id_jugador'] == 8
    assert response.json()['nombre'] == "Jugador4"
    # Test exitoso: Se unio un jugador a una partida existente


def test_post_403(test_data):
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/2/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 403
    assert len(response.json()) == 1
    # Test exitoso: Se rechazo la peticion de unir un jugador a una partida llena


def test_post_404(test_data):
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/3/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 404
    assert len(response.json()) == 1
    # Test exitoso: Se devolvio 404 not found a la peticion de unir un jugador a una partida inexistente

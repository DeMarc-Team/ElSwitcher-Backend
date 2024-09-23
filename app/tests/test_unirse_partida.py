from tests_setup import client, TestingSessionLocal
from models import Jugador
from models import Partida

import pytest


@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()

    partida1 = Partida(nombre_partida="partida_para_unirse",
                       nombre_creador="Creador1")
    db.add(partida1)
    db.flush()  # Para obtener el ID de 'partida1'

    creador1 = Jugador(nombre="Creador1", partida_id=partida1.id, es_creador=True)
    jugador12 = Jugador(nombre="Jugador2", partida_id=partida1.id)
    jugador13 = Jugador(nombre="Jugador3", partida_id=partida1.id)

    db.add(creador1)
    db.add(jugador12)
    db.add(jugador13)

    partida2 = Partida(nombre_partida="partida_llena",
                       nombre_creador="Creador2")
    db.add(partida2)
    db.flush()

    creador2 = Jugador(nombre="Creador2", partida_id=partida2.id, es_creador=True)
    jugador22 = Jugador(nombre="Jugador2", partida_id=partida2.id)
    jugador23 = Jugador(nombre="Jugador3", partida_id=partida2.id)
    jugador24 = Jugador(nombre="Jugador4", partida_id=partida2.id)

    db.add(creador2)
    db.add(jugador22)
    db.add(jugador23)
    db.add(jugador24)

    db.commit()
    db.flush()

    yield db

    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.commit()
    db.flush()
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

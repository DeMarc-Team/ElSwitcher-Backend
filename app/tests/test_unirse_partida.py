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
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 2, f"Fallo: Se esperaba 2 jugadores, pero se obtuvieron {len(response.json())}"
    assert response.json()['id_jugador'] == 8, f"Fallo: Se esperaba el id 8, pero se obtuvo {response.json()['id_jugador']}"
    assert response.json()['nombre'] == "Jugador4", f"Fallo: Se esperaba Jugador4, pero se obtuvo {response.json()['nombre']}"
    # Test exitoso: Se unio un jugador a una partida existente


def test_post_403(test_data):
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/2/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Test exitoso: Se rechazo la peticion de unir un jugador a una partida llena


def test_post_404(test_data):
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/3/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Test exitoso: Se devolvio 404 not found a la peticion de unir un jugador a una partida inexistente

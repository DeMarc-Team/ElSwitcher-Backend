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


def test_unirse_partida_200(test_data):
    '''Test al unirse a una partida existente no llena'''
    body = {"nombre": "Jugador4"}
    response = client.post("partidas/1/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 2, f"Fallo: Se esperaba 2 jugadores, pero se obtuvieron {len(response.json())}"
    assert response.json()['id_jugador'] == 8, f"Fallo: Se esperaba el id 8, pero se obtuvo {response.json()['id_jugador']}"
    assert response.json()['nombre'] == "Jugador4", f"Fallo: Se esperaba Jugador4, pero se obtuvo {response.json()['nombre']}"
    # Test exitoso: Se respondio correctamente
    
    response = client.get("partidas/1/jugadores")
    assert len(response.json()) == 4, f"Fallo: Se esperaba 4 jugadores, pero se obtuvieron {len(response.json())}"
    assert response.json()[3]['nombre'] == "Jugador4", f"Fallo: Se esperaba Jugador4, pero se obtuvo {response.json()[3]['nombre']}"
    # Test exitoso: Se actualizo la db correctamente


def test_unirse_partida_403(test_data):
    '''Test al unirse a una partida llena'''
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/2/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Test exitoso: Se respondio correctamente
    
    response = client.get("partidas/1/jugadores")
    assert len(response.json()) == 3, f"Fallo: Se esperaba 3 jugadores, pero se obtuvieron {len(response.json())}"
    # Test exitoso: No se afecto a la db incorrectamente


def test_unirse_partida_404(test_data):
    '''Test al unirse a una partida inexistente'''
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/3/jugadores", json=body)
    print(f"Response: {response.json()}")
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Test exitoso: Se respondio correctamente
    
    response = client.get("partidas/1/jugadores")
    assert len(response.json()) == 3, f"Fallo: Se esperaba 3 jugadores, pero se obtuvieron {len(response.json())}"
    # Test exitoso: No se afecto a la db incorrectamente
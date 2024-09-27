from tests_setup import client, TestingSessionLocal
from models import Jugador
from models import Partida

import pytest


@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()

    partida1 = Partida(nombre_partida="partida_para_unirse",
                       nombre_creador="Creador1")
    creador1 = Jugador(nombre="Creador1", partida_id=1, es_creador=True)
    jugador12 = Jugador(nombre="Jugador2", partida_id=1)
    jugador13 = Jugador(nombre="Jugador3", partida_id=1)
    
    db.add(partida1)
    db.add(creador1)
    db.add(jugador12)
    db.add(jugador13)

    partida2 = Partida(nombre_partida="partida_llena",
                       nombre_creador="Creador2")
    creador2 = Jugador(nombre="Creador2", partida_id=2, es_creador=True)
    jugador22 = Jugador(nombre="Jugador2", partida_id=2)
    jugador23 = Jugador(nombre="Jugador3", partida_id=2)
    jugador24 = Jugador(nombre="Jugador4", partida_id=2)

    db.add(partida2)
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
    # Verificamos la respuesta del servidor
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 2, f"Fallo: Se esperaba 2 jugadores, pero se obtuvieron {len(response.json())}"
    assert response.json()['id_jugador'] == 8, f"Fallo: Se esperaba el id 8, pero se obtuvo {response.json()['id_jugador']}"
    assert response.json()['nombre'] == "Jugador4", f"Fallo: Se esperaba Jugador4, pero se obtuvo {response.json()['nombre']}"
    # Verificamos que se haya actualizado la db
    db = test_data
    jugadores = db.query(Jugador).filter(Jugador.partida_id == 1).all()
    assert len(jugadores) == 4, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    db.close()


def test_unirse_partida_403(test_data):
    '''Test al unirse a una partida llena'''
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/2/jugadores", json=body)
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Verificamos que no se haya actualizado la db
    db = test_data
    jugadores = db.query(Jugador).filter(Jugador.partida_id == 2).all()
    assert len(jugadores) == 4, f"Fallo: Se esperaban 4 jugadores, pero se obtuvieron {len(jugadores)}"
    db.close()

def test_unirse_partida_404(test_data):
    '''Test al unirse a una partida inexistente'''
    body = {"nombre": "Jugador5"}
    response = client.post("partidas/3/jugadores", json=body)
    print(f"Response: {response.json()}")
    # Verificamos la respuesta del servidor
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"
    # Verificamos que no se haya actualizado la db
    db = test_data
    jugadores = db.query(Jugador).filter(Jugador.partida_id == 3).all()
    assert len(jugadores) == 0, f"Fallo: Se esperaban 0 jugadores, pero se obtuvieron {len(jugadores)}"
    db.close()
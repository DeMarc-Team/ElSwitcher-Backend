from tests_setup import client, TestingSessionLocal
from models import Jugador
from models import Partida

import pytest

# Decorador "fixture" para preparar el entorno de prueba. 
@pytest.fixture(scope="function")
def test_data():
    # Cargamos en la db de prueba una partida con dos jugadores
    db = TestingSessionLocal()

    partida = Partida(nombre_partida="nombre_partida", nombre_creador="Creador", iniciada=False)
    db.add(partida)
    db.flush()
    
    creador = Jugador(nombre="Creador", partida_id=partida.id, es_creador=True)
    jugador1 = Jugador(nombre="Jugador1", partida_id=partida.id)
    jugador2 = Jugador(nombre="Jugador2", partida_id=partida.id)

    db.add(creador)
    db.add(jugador1)
    db.add(jugador2)

    db.commit()
    db.flush()
    db.close()

    # Cerramos la sesión antes de salir del fixture
    yield  db # Este es el punto donde se ejecutan las pruebas

    # Limpiamos la base de datos después de la prueba
    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.commit()
    db.flush()
    db.close()


def test_get_jugadores_200(test_data):
    # Llamamos al endpoint para obtener jugadores de la partida con ID 1 (existente)
    response = client.get("partidas/1/jugadores")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 3, f"Fallo: Se esperaban 3 jugadores, pero se obtuvieron {len(response.json())}"
    assert response.json()[0]['nombre'] == "Creador", f"Fallo: Se esperaba Creador, pero se obtuvo {response.json()[0]['nombre']}"
    assert response.json()[1]['nombre'] == "Jugador1", f"Fallo: Se esperaba Jugador1, pero se obtuvo {response.json()[1]['nombre']}"
    assert response.json()[2]['nombre'] == "Jugador2", f"Fallo: Se esperaba Jugador2, pero se obtuvo {response.json()[2]['nombre']}"
    #Test exitoso: Se obtuvieron los jugadores de una partida existente

def test_get_jugadores_404():
    # Llamamos al endpoint para obtener jugadores de la partida con ID 2 (inexistente)
    response = client.get("partidas/2/jugadores")
    print(f"Response: {response.json()}")
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 jugador, pero se obtuvieron {len(response.json())}"
    #Test exitoso: Se devolvio 404 not found a la peticion de los jugadores de una partida inexistente

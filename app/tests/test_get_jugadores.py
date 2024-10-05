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

    yield  db
    db.close()



def test_get_jugadores_200(test_data):
    # Llamamos al endpoint para obtener jugadores de la partida con ID 1 (existente)
    response = client.get("partidas/1/jugadores")
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 3, f"Fallo: Se esperaban 3 jugadores, pero se obtuvieron {len(response.json())}"
    respuesta_esperada = [{'nombre': 'Creador', 'id_jugador': 1},
                          {'nombre': 'Jugador1', 'id_jugador': 2},
                          {'nombre': 'Jugador2', 'id_jugador': 3}]
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_get_jugadores_404():
    # Llamamos al endpoint para obtener jugadores de la partida con ID 2 (inexistente)
    response = client.get("partidas/2/jugadores")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 2 no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
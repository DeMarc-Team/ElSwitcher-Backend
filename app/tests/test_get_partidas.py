from tests_setup import client, TestingSessionLocal
from models import Partida
from models import Jugador
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

def test_get_partidas(test_data):
    response = client.get("partidas") 
    print(f"Response: {response.json()}")
    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1 ,  f"Fallo: Se esperaba 1 partida, pero se obtuvo {len(response_data)}"
    assert response.json()[0]['nombre_partida'] == "nombre_partida"
    print("Test exitoso")
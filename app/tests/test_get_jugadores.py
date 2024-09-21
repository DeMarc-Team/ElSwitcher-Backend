from tests_setup import client, TestingSessionLocal
from models.jugadores import Jugador
from models.partidas import Partida

import pytest

# Decorador "fixture" para preparar el entorno de prueba. 
# scope="function" significa que se ejecutará antes de cada función de prueba.
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


def test_get_jugadores(test_data):
    # Llamamos al endpoint para obtener jugadores de la partida con ID 1
    response = client.get("partidas/1/jugadores")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['nombre'] == "Jugador1"
    assert response.json()[1]['nombre'] == "Jugador2"
    print("Test exitoso")

# No crear archivos llamados test_ que no sean de tests con pytest
# No crear test con pytest si su nombre no inicia con test_

# En pytest, no necesitas llamar explícitamente a las funciones de prueba.
# El propio pytest se encarga de descubrir y ejecutar las funciones que comienzan
# con test_

# La función de prueba test_get_jugadores tiene como parámetro test_data, 
# que es tu fixture. pytest detecta que necesitas esa fixture y la ejecuta 
# automáticamente antes de ejecutar test_get_jugadores. 
# Esto prepara el entorno de prueba (crea y carga datos en la base de datos).
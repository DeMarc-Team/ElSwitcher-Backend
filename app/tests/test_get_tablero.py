import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import *
from tests_setup import client, TestingSessionLocal
import mock
import json

tablero_mock = json.dumps([[1, 2, 3, 4, 1, 2], [1, 2, 3, 4, 1, 2], [1, 2, 3, 4, 1, 2], [1, 2, 3, 4, 1, 2], [1, 2, 3, 4, 1, 2], [1, 2, 3, 4, 1, 2]])

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

    # Iniciar la partida y crear el juego
    partida.iniciada = True
    juego = Juego(partida_id=partida.id)
    db.add(juego)

    db.commit()
    db.close()

    # Cerramos la sesión antes de salir del fixture
    yield db  # Este es el punto donde se ejecutan las pruebas

    # Limpiamos la base de datos después de la prueba
    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.query(Juego).delete()
    db.query(CartaFigura).delete()
    db.query(CartaMovimiento).delete()
    db.commit()
    db.close()

@mock.patch('crud.juego.get_tablero', mock.Mock(return_value=tablero_mock))
def test_get_tablero_200(test_data):
    # Llamamos al endpoint para obtener el tablero de la partida con ID 1 (existente)
    response = client.get("juego/1/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert json.dumps(response.json()) == tablero_mock, f"Fallo: Se esperaba el tablero {tablero_mock}, pero se obtuvo {response.json()}"

def test_get_tablero_404(test_data):
    response = client.get("juego/2/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"

def test_get_tablero_format(test_data):
    response = client.get("juego/1/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    tablero = response.json()
    assert isinstance(tablero, list), f"Fallo: Se esperaba una lista, pero se obtuvo {type(tablero)}"
    assert all(isinstance(row, list) for row in tablero), "Fallo: Se esperaba que cada fila del tablero fuera una lista"
    assert all(isinstance(cell, int) for row in tablero for cell in row), "Fallo: Se esperaba que cada celda del tablero fuera un entero"
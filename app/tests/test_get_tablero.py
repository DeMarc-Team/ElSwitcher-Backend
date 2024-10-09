
from factory import crear_partida, unir_jugadores, iniciar_partida

from tests_setup import client
import mock
import json

tablero_mock = json.dumps([
        [2, 2, 2, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 2, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2],
        [1, 1, 1, 4, 1, 2]
        ]
)

resaltadas_en_el_mock = {
    "figuras_a_resaltar": {
        "f1": [[[0, 1], [2, 1], [0, 0], [1, 1], [0, 2]]],
        "f2": [],
        "f3": [],
        "f4": [],
    }
}


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

    db.commit()

    yield db
    db.close()

@mock.patch('crud.juego.get_tablero', mock.Mock(return_value=tablero_mock))
def test_get_tablero_200(test_db):
    '''Test para obtener el tablero de una partida.'''

    # Creamamos una partida con 3 jugadores
    partida, _ = crear_partida(db=test_db, nombre_partida="nombre_partida", nombre_creador="Creador")
    unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)
    iniciar_partida(db=test_db, partida=partida)

    # Llamamos al endpoint para obtener el tablero de la partida con ID 1 (existente)
    response = client.get("juego/1/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert json.dumps(response.json()['tablero']) == tablero_mock, f"Fallo: Se esperaba el tablero {tablero_mock}, pero se obtuvo {response.json()}"
    assert json.dumps(response.json()['figuras_a_resaltar']) != [], f"Fallo: Se esperaba el tablero {tablero_mock}, pero se obtuvo {response.json()}"

    for figura in resaltadas_en_el_mock["figuras_a_resaltar"]:
        for coordenadas in resaltadas_en_el_mock["figuras_a_resaltar"][figura]:
            assert coordenadas in response.json()['figuras_a_resaltar'][figura], f"Fallo: Se esperaba que las coordenadas {coordenadas} estuvieran en las resaltadas"


def test_get_tablero_404(test_data):
    response = client.get("juego/2/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 mensaje de error, pero se obtuvieron {len(response.json())}"

def test_get_tablero_format(test_data):
    response = client.get("juego/1/tablero")
    print(f"Response: {response.json()}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    tablero = response.json()['tablero']
    assert isinstance(tablero, list), f"Fallo: Se esperaba una lista, pero se obtuvo {type(tablero)}"
    assert all(isinstance(row, list) for row in tablero), "Fallo: Se esperaba que cada fila del tablero fuera una lista"
    assert all(isinstance(cell, int) for row in tablero for cell in row), "Fallo: Se esperaba que cada celda del tablero fuera un entero"

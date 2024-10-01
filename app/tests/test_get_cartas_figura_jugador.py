from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador, CartaFigura
import mock
import pytest
from os import remove

import pdb

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()

    yield db

    try:
        db.query(Jugador).delete()
        db.query(CartaFigura).delete()
        db.query(Juego).delete()
        db.query(Partida).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()




# Tests
"""
Se crea una partida
Y se inicia para ver si el jugador recibio las cartas
"""
@mock.patch('models.CartaFigura.random_figura', mock.Mock(return_value='f1'))
def test_get_cartas_figura_jugador(test_db):
    # Access the test_db to avoid the unused fixture warning
    nueva_partida = {
        'nombre_partida': 'partida1',
        'nombre_creador': 'Demetrio'
    }

    # Crear una partida
    response = client.post("/partidas", json=nueva_partida)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Crear un jugador en la partida
    id_partida = response.json()['id']
    print(f"Id partida creada: {id_partida}")
    player = {'nombre': 'Riquelme'}
    response = client.post(f"/partidas/{id_partida}/jugadores", json=player)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    # Iniciar la partida y ver las cartas del jugador creado
    player_id = response.json()['id_jugador']
    print(player_id)
    print(id_partida)
    response = client.put(f"partidas/{id_partida}")

    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    response = client.get(f"/juego/{id_partida}/jugadores/{player_id}/cartas_figura")

    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    cartas = response.json()

    for carta in cartas:
        assert carta['figura'] == 'f1', f"Fallo: Se esperaba la figura f1, pero se obtuvo {carta['figura']}"

def test_get_cartas_figura_jugador_diferentes_figuras(test_db):
    with mock.patch('models.CartaFigura.random_figura', mock.Mock(side_effect=['f1', 'f2', 'f3','f1', 'f2', 'f3'])):
        assert test_db is not None
        nueva_partida = {
            'nombre_partida': 'partida4',
            'nombre_creador': 'Juan'
        }

        response = client.post("/partidas", json=nueva_partida)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
        id_partida = response.json()['id']
        print(f"Id partida creada: {id_partida}")
        player = {'nombre': 'Zidane'}
        response = client.post(f"/partidas/{id_partida}/jugadores", json=player)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

        player_id = response.json()['id_jugador']
        print(player_id)
        print(id_partida)
        response = client.put(f"partidas/{id_partida}")
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

        response = client.get(f"/juego/{id_partida}/jugadores/{player_id}/cartas_figura")
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

        cartas = response.json()
        figuras_esperadas = ['f1', 'f2', 'f3']
        for i, carta in enumerate(cartas):
            assert carta['figura'] == figuras_esperadas[i], f"Fallo: Se esperaba la figura {figuras_esperadas[i]}, pero se obtuvo {carta['figura']}"


def test_get_cartas_figura_jugador_con_creador_y_otro_jugador(test_db):
    with mock.patch('models.CartaFigura.random_figura', mock.Mock(return_value='f1')):
        assert test_db is not None
        nueva_partida = {
            'nombre_partida': 'partida5',
            'nombre_creador': 'Pedro'
        }

        # Crear una partida
        response = client.post("/partidas", json=nueva_partida)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        
        id_partida = response.json()['id']
        print(f"Id partida creada: {id_partida}")

        # Añadir el creador como jugador
        creador = {'nombre': 'Pedro'}
        response = client.post(f"/partidas/{id_partida}/jugadores", json=creador)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        creador_id = response.json()['id_jugador']
        print(f"Id creador: {creador_id}")

        # Añadir otro jugador
        otro_jugador = {'nombre': 'Gonzalo'}
        response = client.post(f"/partidas/{id_partida}/jugadores", json=otro_jugador)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        otro_jugador_id = response.json()['id_jugador']
        print(f"Id otro jugador: {otro_jugador_id}")

        # Iniciar la partida
        response = client.put(f"partidas/{id_partida}")
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

        # Verificar las cartas del creador
        response = client.get(f"/juego/{id_partida}/jugadores/{otro_jugador_id}/cartas_figura")
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        cartas_creador = response.json()
        for carta in cartas_creador:
            assert carta['figura'] == 'f1', f"Fallo: Se esperaba la figura f1, pero se obtuvo {carta['figura']}"

        # Verificar las cartas del otro jugador
        response = client.get(f"/juego/{id_partida}/jugadores/{otro_jugador_id}/cartas_figura")
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        cartas_otro_jugador = response.json()
        for carta in cartas_otro_jugador:
            assert carta['figura'] == 'f1', f"Fallo: Se esperaba la figura f1, pero se obtuvo {carta['figura']}"


def test_get_cartas_figura_jugador_sin_cartas(test_db):
    assert test_db is not None
    nueva_partida = {
        'nombre_partida': 'partida6',
        'nombre_creador': 'Luis'
    }

    # Crear una partida
    response = client.post("/partidas", json=nueva_partida)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    id_partida = response.json()['id']
    print(f"Id partida creada: {id_partida}")

    # Añadir el creador como jugador
    creador = {'nombre': 'Luis'}
    response = client.post(f"/partidas/{id_partida}/jugadores", json=creador)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    creador_id = response.json()['id_jugador']
    print(f"Id creador: {creador_id}")

    # Añadir otro jugador
    otro_jugador = {'nombre': 'Miguel'}
    response = client.post(f"/partidas/{id_partida}/jugadores", json=otro_jugador)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    otro_jugador_id = response.json()['id_jugador']
    print(f"Id otro jugador: {otro_jugador_id}")

    # Verificar que el creador no tiene cartas
    response = client.get(f"/juego/{id_partida}/jugadores/{otro_jugador_id}/cartas_figura")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    cartas_creador = response.json()
    assert len(cartas_creador) == 0, f"Fallo: Se esperaba una lista vacía, pero se obtuvo {cartas_creador}"

    # Verificar que el otro jugador no tiene cartas
    response = client.get(f"/juego/{id_partida}/jugadores/{otro_jugador_id}/cartas_figura")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    cartas_otro_jugador = response.json()
    assert len(cartas_otro_jugador) == 0, f"Fallo: Se esperaba una lista vacía, pero se obtuvo {cartas_otro_jugador}"
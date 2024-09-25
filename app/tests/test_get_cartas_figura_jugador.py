from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador, CartaFigura, Juego
import mock
import pytest
from os import remove

import pdb

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()

    yield db

    try:
        db.query(CartaFigura).delete()
        db.query(Jugador).delete()
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
@mock.patch('crud.partidas.random_figura', mock.Mock(return_value='f1'))

def test_get_cartas_figura_jugador(test_db):
    # Access the test_db to avoid the unused fixture warning
    assert test_db is not None
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
    response = client.put(f"/partidas/{{partida_id: int}}?partida_id={id_partida}")

    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    response = client.get(f"/partidas/juego/{{partida_id: int}}/jugadores/{{jugador_id: int}}/cartas_figura?partida_id={id_partida}&jugador_id={player_id}")

    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"

    cartas = response.json()

    for carta in cartas:
        assert carta['figura'] == 'f1', f"Fallo: Se esperaba la figura f1, pero se obtuvo {carta['figura']}"

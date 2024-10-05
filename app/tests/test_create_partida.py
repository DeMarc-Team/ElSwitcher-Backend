from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador
import pytest

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()

def test_create_partida(test_db):
    '''Test para crear una partida'''
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post("/partidas", json=nueva_partida)
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {  'nombre_partida': 'Partida_nueva',
                            'nombre_creador': 'Jugador_nuevo',
                            'id': 1,
                            'id_creador': 1,
                            'iniciada': False}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

    # Verificamos que la partida se haya creado correctamente en la db
    db = test_db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    print(partida)
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    assert partida.iniciada == False, f"Fallo: Se esperaba False como estado de la partida, pero se obtuvo {partida.iniciada}"
    assert len(partida.jugadores) == 1, f"Fallo: Se esperaba 1 jugador en la partida, pero se obtuvo {len(partida.jugadores)}"
    
    db.close()
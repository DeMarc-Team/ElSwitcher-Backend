from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador
import pytest

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    yield db
    db.query(Partida).delete()
    db.query(Jugador).delete()
    db.commit()
    db.flush()
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
    response_data = response.json()
    assert response_data['nombre_partida'] == "Partida_nueva", f"Fallo: Se obtuvo {response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {response_data['nombre_creador']} como nombre del creador de la partida"
    
    # Verificamos que la partida se haya creado correctamente en la db
    db = test_db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    db.close()

def test_create_partida_long_name(test_db):
    '''Test para crear una partida con un nombre muy largo'''
    # Datos para el cuerpo del post
    nueva_partida = {
        "nombre_partida": "emi"*10000000,
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post("/partidas", json=nueva_partida)
    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {
        response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "emi"*10000000, f"Fallo: Se obtuvo {
        response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {
        response_data['nombre_creador']} como nombre del creador de la partida"
    # Verificamos que la partida se haya creado correctamente en la db
    db = test_db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    assert partida.nombre_partida == "emi"*10000000, f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {
        partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {
        partida.nombre_creador}"
    db.close()
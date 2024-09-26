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
    # Datos para el cuerpo del post
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }

    response = client.post("/partidas", json=nueva_partida)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "Partida_nueva", f"Fallo: Se obtuvo {response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {response_data['nombre_creador']} como nombre del creador de la partida"
    
    response = client.get("partidas/1/jugadores")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert len(response.json()) == 1, f"Fallo: Se esperaba 1 jugador, pero se obtuvieron {len(response.json())}"
    assert response.json()[0]['nombre'] == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo, pero se obtuvo {response.json()[0]['nombre']}"
    # Test exitoso: Se creo una partida y se unio el jugador a la misma 

def test_create_partida_long_name(test_db):
    # Datos para el cuerpo del post
    nueva_partida = {
        "nombre_partida": "emi"*10000000,
        "nombre_creador": "Jugador_nuevo"
    }

    response = client.post("/partidas", json=nueva_partida)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {
        response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "emi"*10000000, f"Fallo: Se obtuvo {
        response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {
        response_data['nombre_creador']} como nombre del creador de la partida"
    print("Test exitoso")
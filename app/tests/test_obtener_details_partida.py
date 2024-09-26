from tests_setup import client, TestingSessionLocal
from models import Partida
from models import Jugador
import pytest

@pytest.fixture(scope="function")
def test_data():
    db = TestingSessionLocal()

    partida = Partida(nombre_partida="partida_details", nombre_creador="Creador")
    jugador1 = Jugador(nombre="Creador", es_creador=True, partida_id=1)
    jugador2 = Jugador(nombre="Jugador", es_creador=False, partida_id=1)
    
    db.add(partida)
    db.add(jugador1)
    db.add(jugador2)
    db.commit()
    db.flush()
    db.close()

    yield  db

    db.query(Jugador).delete()
    db.query(Partida).delete()
    db.commit()
    db.flush()
    db.close()

def test_get_details_partida_200(test_data):
    response = client.get("partidas/1") 
    print(f"Response: {response.json()}")
    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    assert response.json()['id'] == 1, f"Fallo: Se esperaba 1, pero se obtuvo {response.json()['id']}"
    assert response.json()['nombre_partida'] == "partida_details", f"Fallo: Se esperaba 'partida_details', pero se obtuvo {response.json()[0]['nombre_partida']}"
    assert response.json()['nombre_creador'] == "Creador", f"Fallo: Se esperaba 'Creador', pero se obtuvo {response.json()[0]['nombre_creador']}"
    assert response.json()['id_creador'] == 1, f"Fallo: Se esperaba 1, pero se obtuvo {response.json()[0]['id_creador']}"
    assert response.json()['iniciada'] == False, f"Fallo: Se esperaba False, pero se obtuvo {response.json()[0]['iniciada']}"
    assert response.json()['espacios_disponibles'] == 2, f"Fallo: Se esperaba 2, pero se obtuvo {response.json()[0]['espacios_disponibles']}"

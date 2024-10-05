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

    yield  db

    db.close()


def test_get_details_partida_200(test_data):
    response = client.get("partidas/1") 
    print(f"Response: {response.json()}")

    assert response.status_code == 200 , f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'nombre_partida': 'partida_details',
                          'nombre_creador': 'Creador',
                          'id': 1,
                          'id_creador': 1,
                          'iniciada': False,
                          'espacios_disponibles': 2}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"

# ----------------------------------------------------------------

def test_get_details_partida_404(test_data):
    response = client.get("partidas/2") 
    print(f"Response: {response.json()}")
    
    assert response.status_code == 404 , f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    respuesta_esperada = {'detail': 'Partida con ID 2 no encontrada.'}
    assert response.json() == respuesta_esperada, f"Fallo: Se esperaba {respuesta_esperada} como respuesta, pero se obtuvo {response.json()}"
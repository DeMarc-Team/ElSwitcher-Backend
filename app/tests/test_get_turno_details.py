from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador, CartaFigura, CartaMovimiento
from crud.juego import siguiente_turno
import pytest

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    
    yield db

    db.close()
        
def test_get_turno_details(test_db):
    '''Test para crear iniciar una partida con un juego asociado'''
    db = test_db
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post("/partidas", json=nueva_partida)
    db.commit()
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "Partida_nueva", f"Fallo: Se obtuvo {response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {response_data['nombre_creador']} como nombre del creador de la partida"
    
    # Verificamos que la partida se haya creado correctamente en la db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    
    # Añadimos otro jugador a la partida para poder iniciarla
    otro_jugador = {
        "nombre": "Otro_jugador"
    }
    
    response = client.post(f'/partidas/{partida.id}/jugadores', json=otro_jugador)
    db.commit()
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Iniciamos la partida
    response = client.put(f"/partidas/{partida.id}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Verificamos el funcionamiento del endpoint según la especificación de la api
    datos_turno = {
        "id_jugador": partida.jugador_id,
        "nombre_jugador": partida.jugador_del_turno.nombre
    }
    
    response = client.get(f'/juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    assert response.json() == datos_turno

def test_casos_prohibidos(test_db):
    '''Test para verificar que estén cubiertos los casos prohibidos especificados en la api'''
    db = test_db
    # Verificamos que no se pueda acceder a la información del turno en una partida inexistente
    response = client.get(f'/juego/1/turno')
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post("/partidas", json=nueva_partida)
    db.commit()
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "Partida_nueva", f"Fallo: Se obtuvo {response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {response_data['nombre_creador']} como nombre del creador de la partida"
    
    # Verificamos que la partida se haya creado correctamente en la db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    
    # Verificamos que no se pueda acceder a la información del turno en una partida no iniciada
    response = client.get(f'/juego/{partida.id}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"

def test_siguiente_turno(test_db):
    '''Test para verificar el correcto funcionamiento de la lista ordenada de turnos'''
    db = test_db
    nueva_partida = {
        "nombre_partida": "Partida_nueva",
        "nombre_creador": "Jugador_nuevo"
    }
    response = client.post("/partidas", json=nueva_partida)
    db.commit()
    print(f"Response: {response.json()}")

    # Verificamos que la respuesta sea la esperada
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    response_data = response.json()
    assert response_data['nombre_partida'] == "Partida_nueva", f"Fallo: Se obtuvo {response_data['nombre']} como nombre de la partida"
    assert response_data['nombre_creador'] == "Jugador_nuevo", f"Fallo: Se obtuvo {response_data['nombre_creador']} como nombre del creador de la partida"
    
    # Verificamos que la partida se haya creado correctamente en la db
    partida = db.query(Partida).filter(Partida.id == 1).first()
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    
    # Añadimos otro jugador a la partida para poder iniciarla
    otro_jugador = {
        "nombre": "Otro_jugador"
    }
    
    response = client.post(f'/partidas/{partida.id}/jugadores', json=otro_jugador)
    db.commit()
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Iniciamos la partida
    response = client.put(f"/partidas/{partida.id}")
    db.commit()
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Obtenemos el jugador actual
    response = client.get(f'/juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    id_primer_jugador = response.json()['id_jugador']
    
    # Cambiamos al siguiente jugador
    response = client.put(f'/juego/{partida.id}/jugadores/{id_primer_jugador}/turno')
    db.commit()
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}" 
    
    # Obtenemos el nuevo jugador actual
    response = client.get(f'/juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    id_segundo_jugador = response.json()['id_jugador']
    
    # Verificamos que los ids sean distintos
    assert id_primer_jugador != id_segundo_jugador
    
    # Forzamos nuevamente el cambio al siguiente jugador
    siguiente_turno(db, partida.id)
    db.refresh(partida)
    
    # Obtenemos el nuevo jugador actual
    tercer_id = response.json()['id_jugador']
    
    # Verificamos que se vuelva al primer turno
    assert id_primer_jugador != tercer_id
    
    
    
    
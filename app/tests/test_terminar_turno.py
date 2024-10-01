from tests_setup import client, TestingSessionLocal
from models import Partida, Jugador, CartaFigura, CartaMovimiento
import pytest

def iniciar_partida_de_cuatro(db):
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
    partida = db.query(Partida).filter(Partida.id == 1).first()
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    
    # Añadimos otros jugadores a la partida
    otros_jugadores = [{"nombre": f"jugador{i}"} for i in range(0,3)]
    
    for jugador in otros_jugadores:
        response = client.post(f'/partidas/{partida.id}/jugadores', json=jugador)
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    # Iniciamos la partida
    response = client.put(f"/partidas/{partida.id}")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    
    return partida
   
def crear_partida_sin_iniciar(db):
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
    partida = db.query(Partida).filter(Partida.id == 1).first()
    
    assert partida.nombre_partida == "Partida_nueva", f"Fallo: Se esperaba Partida_nueva como nombre de la partida, pero se obtuvo {partida.nombre_partida}"
    assert partida.nombre_creador == "Jugador_nuevo", f"Fallo: Se esperaba Jugador_nuevo como nombre del creador de la partida, pero se obtuvo {partida.nombre_creador}"
    
    return partida

@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    
    # Se limpia lo que tenía anteriormente la base de datos
    try:
        db.query(CartaFigura).delete()
        db.query(CartaMovimiento).delete()
        db.query(Jugador).delete()
        db.query(Partida).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    
    partida_sin_iniciar = crear_partida_sin_iniciar(db)
    partida_de_cuatro = iniciar_partida_de_cuatro(db)

    yield db, partida_de_cuatro, partida_sin_iniciar

    # Se limpia lo que quedó en la base de datos
    try:
        db.query(CartaFigura).delete()
        db.query(CartaMovimiento).delete()
        db.query(Jugador).delete()
        db.query(Partida).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def test_terminar_turno(test_db):
    '''Test sobre el funcionamiento de terminar un turno'''
    db, partida, _ = test_db

    # Refrescamos el objeto de la partida luego de los cambios en la db
    db.refresh(partida)

    
    # Verificamos que la partida esté iniciada
    assert partida.iniciada
    
    # Obtenemos el id del jugador que tiene el primer turno
    response = client.get(f'juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    id_jugador_inicial = response.json()['id_jugador']
    id_jugador_anterior = None

    for i in range(0, len(partida.jugadores)):
        # Obtenemos el id del jugador actual
        response = client.get(f'juego/{partida.id}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        id_jugador_actual = response.json()['id_jugador']

        # Verificamos que efectivamente se haya cambiador el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."
        
        id_jugador_anterior = id_jugador_actual
        
        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')

    # Obtenemos el id del nuevo jugador actual
    response = client.get(f'juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    id_jugador_actual = response.json()['id_jugador']
        
    # Verificamos que los turnos "hayan dado la vuelta completa"
    assert id_jugador_inicial == id_jugador_actual

def test_varias_rondas(test_db):
    '''Test sobre la confiabilidad de una ronda de turnos.'''
    db, partida, _ = test_db
    
    # Refrescamos el objeto de la partida luego de los cambios en la db
    db.refresh(partida)
    
    # Verificamos que la partida esté iniciada
    assert partida.iniciada
    
    # Obtenemos el id del jugador que tiene el primer turno
    response = client.get(f'juego/{partida.id}/turno')
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    id_jugador_inicial = response.json()['id_jugador']
    
    orden_de_turnos = []
    id_jugador_anterior = None
    # Hacemos una primera ronda para identificar el orden por id
    for i in range(0, len(partida.jugadores)):
        
        # Obtenemos el id del jugador actual
        response = client.get(f'juego/{partida.id}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        id_jugador_actual = response.json()['id_jugador']
        
        # Verificamos que efectivamente se haya cambiador el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."
        
        orden_de_turnos.append(id_jugador_actual)
        id_jugador_anterior = id_jugador_actual
        
        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')

    # Hacemos 4 rondas mas para ver si tal orden se mantiene
    for i in range(0, 4 * len(partida.jugadores)):
        
        # Obtenemos el id del jugador actual
        response = client.get(f'juego/{partida.id}/turno')
        assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
        id_jugador_actual = response.json()['id_jugador']
        
        # Verificamos que efectivamente se haya cambiador el turno
        assert id_jugador_actual != id_jugador_anterior, f"Fallo: Se esperaba un cambio de turno en el jugador {id_jugador_actual}, pero esto no ocurrió."
        
        assert orden_de_turnos[i%4] == id_jugador_actual
        id_jugador_anterior = id_jugador_actual
        
        # Terminamos el turno del jugador actual
        response = client.put(f'juego/{partida.id}/jugadores/{id_jugador_actual}/turno')

def test_casos_prohibidos(test_db):
    '''Test sobre el la confiabilidad de una ronda de turnos.'''
    db, partida_iniciada, partida_sin_iniciar = test_db
    
    # Intentamos terminar el turno de una partida inexistente.
    response = client.put(f'juego/{999999}/jugadores/{999999}/turno')
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}"
    
    # Intentamos terminar el turno de una partida no iniciada.
    response = client.put(f'juego/{partida_sin_iniciar.id}/jugadores/{999999}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    
    # Intentamos terminar el turno de un jugador que no es el que posee el turno (o no existe).
    response = client.put(f'juego/{partida_iniciada.id}/jugadores/{999999}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    
    
    
    
    
    
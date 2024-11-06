from factory import crear_partida, unir_jugadores, iniciar_partida, siguiente_turno

def test_get_turno_details(client, test_db):
    '''Test sobre la obtención de detalles del turno de una partida iniciada.'''
    
    partida, creador = crear_partida(test_db, nombre_partida="Partida 1", nombre_creador="Creador 1")
    unir_jugadores(test_db, partida=partida, numero_de_jugadores=3)
    iniciar_partida(test_db, partida)
    
    response = client.get(test_db, f"/juego/{partida.id}/turno")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    
    turno_details = response.json()
    
    # Verificamos que se hayan recibido los datos correctos.
    assert turno_details == {
        "id_jugador": creador.id_jugador,
        "nombre_jugador": creador.nombre
    }, f"Fallo: Se esperaba los datos fueran {{'id_jugador': 1, 'nombre_jugador': Creador 1}}, pero son {turno_details}."

def test_partida_sin_iniciar_403(client, test_db):
    '''Test sobre el comportamiento de get_turno_details ante el intento de acceso cuando una partida no está iniciada.'''
    
    partida, _ = crear_partida(test_db)
    unir_jugadores(test_db, partida=partida, numero_de_jugadores=1)
    
    response = client.get(test_db, f'/juego/{partida.id}/turno')
    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}."
    
def test_la_partida_no_existe_404(client, test_db):
    '''Test sobre el comportamiento de get_turno_details ante el intento de acceso cuando una partida no está iniciada.'''
   
    partida_id = 1    
    response = client.get(test_db, f'/juego/{partida_id}/turno')
    
    assert response.status_code == 404, f"Fallo: Se esperaba el estado 404, pero se obtuvo {response.status_code}."
    
def test_cambio_en_el_turno(client, test_db):
    '''Test que revisa la correcta actualización de la informacion de un turno ante un pasaje del mismo.'''
    partida, creador = crear_partida(test_db, nombre_partida="Partida 2", nombre_creador="Creador 2")
    unir_jugadores(test_db, partida=partida, numero_de_jugadores=2)
    iniciar_partida(test_db, partida)
    
    response = client.get(test_db, f"/juego/{partida.id}/turno")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    
    turno_details = response.json()
    
    # Nos aseguramos cual es el valor que se obtiene primero
    assert turno_details == {
        "id_jugador": creador.id_jugador,
        "nombre_jugador": creador.nombre
    }, f"Fallo: Se esperaba los datos fueran {{'id_jugador': 1, 'nombre_jugador': Creador 1}}, pero son {turno_details}."
    
    # Pasamos al siguiente turno
    siguiente_turno(test_db, partida)
    
    # Obtenemos nuevamente la información
    response = client.get(test_db, f"/juego/{partida.id}/turno")
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}."
    
    # Chequeamos que el turno se haya pasado y sea lo unico que cambio
    turno_details = response.json()
    assert turno_details == {
        "id_jugador": 2,
        "nombre_jugador": "Jugador2"
    }, f"Fallo: Se esperaba los datos fueran {{'id_jugador': 1, 'nombre_jugador': Creador 1}}, pero son {turno_details}."

    
    
    
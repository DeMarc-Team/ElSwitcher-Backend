import copy

from factory import crear_partida, unir_jugadores, iniciar_partida
from test_endpoint_jugar_carta_movimiento import agregar_m1_a_los_inventarios, jugar_carta_m1
from websockets_manager.ws_partidas_manager import ACTUALIZAR_TURNO, ACTUALIZAR_TABLERO, ACTUALIZAR_CARTAS_MOVIMIENTO, ACTUALIZAR_SALA_ESPERA
from websockets_manager.ws_home_manager import ACTUALIZAR_PARTIDAS # Hace falta porque un jugador abandona

def test_cancelar_movimiento_parcial(client, test_db, test_ws_counts):
    test_ws_counts[ACTUALIZAR_TABLERO] = 2
    test_ws_counts[ACTUALIZAR_CARTAS_MOVIMIENTO] = 2

    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    tablero_original = copy.copy(partida.tablero)
    tablero_esperado_durante_parcial = '[[3, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 2, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id == id_jugador_del_turno][0]

    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador debería haber jugado su carta de movimiento"

    response = jugar_carta_m1(client, partida, id_jugador_del_turno)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    test_db.refresh(jugador_del_turno) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo

    assert len(partida.movimientos_parciales) == 1, "Fallo: Debería haber un movimiento parcial"
    assert partida.movimientos_parciales[0].origen == str((0,0)), "Fallo: La casilla 1 no es la esperada"
    assert partida.movimientos_parciales[0].destino == str((2,2)), "Fallo: La casilla 2 no es la esperada"
    test_db.refresh(partida) # Sin esto el tablero queda viejo  
    assert partida.tablero == tablero_esperado_durante_parcial, "Fallo: El tablero no es el esperado"

    response = client.delete(f"/juego/{partida.id}/jugadores/{id_jugador_del_turno}/mov-parciales")
    test_db.refresh(partida) # Sin esto el tablero queda viejo  

    assert partida.movimientos_parciales == [], "Fallo: Debería haberse limpiado la lista de movimientos parciales"
    assert partida.tablero == tablero_original, "Fallo: El tablero no debería haber cambiado"
                                                            

def test_no_se_puede_cancelar_movimiento_parcial_si_no_hay_movimientos_parciales(client, test_db, test_ws_counts):
    test_ws_counts[ACTUALIZAR_TABLERO] = 0
    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")

    tablero_original = copy.copy(partida.tablero)
    tablero_esperado_durante_parcial = '[[3, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 2, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id == id_jugador_del_turno][0]

    response = client.delete(f"/juego/{partida.id}/jugadores/{id_jugador_del_turno}/mov-parciales")
    test_db.refresh(partida) # Sin esto el tablero queda viejo  

    assert response.status_code == 403, f"Fallo: Se esperaba el estado 403, pero se obtuvo {response.status_code}"
    assert partida.movimientos_parciales == [], "Fallo: Debería haberse limpiado la lista de movimientos parciales"
    assert partida.tablero == tablero_original, "Fallo: El tablero no debería haber cambiado"

def test_se_limpian_los_movs_parciales_pasando_turno(client, test_db):
    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    tablero_original = copy.copy(partida.tablero)
    tablero_esperado = '[[3, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 2, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id == id_jugador_del_turno][0]

    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador debería haber jugado su carta de movimiento"

    response = jugar_carta_m1(client, partida, id_jugador_del_turno)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    test_db.refresh(jugador_del_turno) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo

    response = client.put(f"/juego/{partida.id}/jugadores/{id_jugador_del_turno}/turno")

    test_db.refresh(partida) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo
    assert partida.tablero == tablero_original, "Fallo: El tablero no debería haber cambiado"
    assert partida.movimientos_parciales == [], "Fallo: Debería haberse limpiado la lista de movimientos parciales"


def test_se_limpian_los_movs_parciales_abandonando(client, test_db, test_ws_counts):
    test_ws_counts[ACTUALIZAR_CARTAS_MOVIMIENTO] = 1 # Se actualizan las cartas de movimiento, pero despues abandona y no hace falta
    test_ws_counts[ACTUALIZAR_TABLERO] = 2 # El tablero se cambia, pero despues se restaura
    test_ws_counts[ACTUALIZAR_TURNO] = 1 # Un jugador abandona y se pasa su turno
    test_ws_counts[ACTUALIZAR_PARTIDAS] = 1 # Un jugador abandona y las partidas se actualizan incondicionalmente
    test_ws_counts[ACTUALIZAR_SALA_ESPERA] = 1 # Igual que arriba
    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    tablero_original = copy.copy(partida.tablero)
    tablero_esperado = '[[3, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 2, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=2)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id == id_jugador_del_turno][0]

    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador debería haber jugado su carta de movimiento"

    response = jugar_carta_m1(client, partida, id_jugador_del_turno)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    test_db.refresh(jugador_del_turno) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo

    response = client.delete(f"/partidas/{partida.id}/jugadores/{id_jugador_del_turno}")

    test_db.refresh(partida) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo
    assert partida.tablero == tablero_original, "Fallo: El tablero no debería haber cambiado"
    assert partida.movimientos_parciales == [], "Fallo: Debería haberse limpiado la lista de movimientos parciales"
import copy
from tests_setup import client
from models import Partida
from factory import crear_partida, unir_jugadores, iniciar_partida, CartaMovimiento
import json
import mock


def test_hacer_movimiento_200(test_db):
    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")
    tablero_original = copy.copy(partida.tablero)
    tablero_esperado = '[[3, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 2, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id_jugador == id_jugador_del_turno][0]

    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador debería haber jugado su carta de movimiento"

    response = jugar_carta_m1(partida, id_jugador_del_turno)
    assert response.status_code == 200, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    test_db.refresh(jugador_del_turno) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo

    assert len(partida.movimientos_parciales) == 1, "Fallo: Debería haber un movimiento parcial"
    assert partida.movimientos_parciales[0].origen == str((0,0)), "Fallo: La casilla 1 no es la esperada"
    assert partida.movimientos_parciales[0].destino == str((2,2)), "Fallo: La casilla 2 no es la esperada"

    test_db.refresh(partida) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo
    assert partida.tablero != tablero_original, "Fallo: El tablero no debería haber cambiado"
    assert partida.tablero == tablero_esperado, "Fallo: El tablero no es el esperado"


def test_movimiento_invalido(test_db):
    partida, creador = crear_partida(db=test_db, nombre_partida="partida_con_2_jugadores", nombre_creador="Creador")

    jugadores = [creador] + unir_jugadores(db=test_db, partida=partida, numero_de_jugadores=1)

    tablero_original = copy.copy(partida.tablero)

    agregar_m1_a_los_inventarios(test_db, 1 ,jugadores)

    iniciar_partida(db=test_db, partida=partida)
    
    # Obtenemos de quien es el turno
    response = client.get(f"/juego/{partida.id}/turno")

    id_jugador_del_turno = response.json()['id_jugador']
    jugador_del_turno = [jugador for jugador in jugadores if jugador.id_jugador == id_jugador_del_turno][0]

    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador debería haber jugado su carta de movimiento"

    response = jugar_movimiento_invalido(partida, id_jugador_del_turno)
    
    assert partida.tablero == tablero_original, "Fallo: El tablero no debería haber cambiado"
    assert partida.movimientos_parciales == [], "Fallo: La casilla 1 no es la esperada"

    assert response.status_code == 403, f"Fallo: Se esperaba el estado 200, pero se obtuvo {response.status_code}"
    test_db.refresh(jugador_del_turno) # Esto es necesario para que el objeto jugador_del_turno se actualice con la base de datos, no supe sacarlo
    assert len(jugador_del_turno.mano_movimientos) == 3, "Fallo: El jugador no debe haber podido descartar su carta"

# Auxiliares
def agregar_m1_a_los_inventarios(test_db, n_m1_a_agregar , jugadores):
    for jugador in jugadores:
        for n_m1_a_agregar in range(n_m1_a_agregar):
            carta = CartaMovimiento(movimientos_de=jugador,movimiento='m1') # Para poder testear hacer movimientos necesito darle una carta que se jugar en el tablero
            test_db.add(carta)
            test_db.commit()

def jugar_carta_m1(partida, id_jugador_del_turno):
    jugada = {
        "casilla1": {
            "row": 0,
            "col": 0
        },
        "casilla2": {
            "row": 2,
            "col": 2
        },
        "codeMove": "m1"
    }
    response = client.put(f"/juego/{partida.id}/jugadores/{id_jugador_del_turno}/tablero/casilla",json=jugada)
    return response

def jugar_movimiento_invalido(partida, id_jugador_del_turno):
    jugada = {
        "casilla1": {
            "row": 0,
            "col": 0
        },
        "casilla2": {
            "row": 89,
            "col": 7
        },
        "codeMove": "m1"
    }
    # Hacemos un movimiento
    response = client.put(f"/juego/{partida.id}/jugadores/{id_jugador_del_turno}/tablero/casilla",json=jugada)
    return response
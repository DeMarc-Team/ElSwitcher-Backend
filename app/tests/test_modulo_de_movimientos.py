import pytest
from services.movimientos import SET_DE_MOVIMIENTOS, is_valid_move, swapear_en_tablero

@pytest.fixture
def tablero():
    return [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

def test_is_valid_move(tablero):
    origen = (2, 2)
    destino = (0, 0)
    movimiento = SET_DE_MOVIMIENTOS[0]  # Movimiento1 with vector (-2, 2)
    
    assert is_valid_move(movimiento, tablero, origen, destino) == True

    destino = (4, 4)
    assert is_valid_move(movimiento, tablero, origen, destino) == True

def test_swapear_en_tablero(tablero):
    origen = (1, 1)
    destino = (2, 2)
    tablero[1][1] = 1
    tablero[2][2] = 2

    swapear_en_tablero(tablero, origen, destino)

    assert tablero[1][1] == 2
    assert tablero[2][2] == 1

def test_is_valid_move_out_of_bounds(tablero):
    origen = (5, 5)
    destino = (5, 7)
    movimiento = SET_DE_MOVIMIENTOS[1]  # Movimiento2 with vector (-2, 0)

    assert is_valid_move(movimiento, tablero, origen, destino) == False

def test_is_valid_move_rotation(tablero):
    origen = (2, 2)
    destino = (4, 0)
    movimiento = SET_DE_MOVIMIENTOS[0]  # Movimiento1 with vector (-2, 2)

    assert is_valid_move(movimiento, tablero, origen, destino) == True
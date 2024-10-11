import pytest
from movimientos import VectorMovimiento, Movimiento, Movimiento1, Movimiento2, Movimiento3, Movimiento4, Movimiento5, Movimiento6, Movimiento7, swapear_en_tablero

def test_vector_movimiento_rotacion():
    vector = VectorMovimiento((1, 0))
    assert vector.rotacion(0) == (1, 0)
    assert vector.rotacion(1) == (0, -1)
    assert vector.rotacion(2) == (-1, 0)
    assert vector.rotacion(3) == (0, 1)
    assert vector.rotacion(4) == (1, 0)

def test_swapear_en_tablero():
    tablero = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    origen = (0, 0)
    destino = (2, 1)
    movimiento = Movimiento6()

    assert swapear_en_tablero(movimiento, tablero, origen, destino) == True
    assert tablero == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 1, 0]
    ]

    destino = (1, 1)
    assert swapear_en_tablero(movimiento, tablero, origen, destino) == False
    assert tablero == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 1, 0]
    ]
def test_movimiento1():
    tablero = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    origen = (0, 0)
    destino = (2, 2)
    movimiento = Movimiento1()

    assert swapear_en_tablero(movimiento, tablero, origen, destino) == True
    assert tablero == [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 1]
    ]

def test_movimiento4():
    tablero = [
        [1, 0, 0],
        [0, 3, 0],
        [0, 0, 1]
    ]

    origen = (1, 1)
    destino = (0, 2)
    movimiento = Movimiento4()

    assert swapear_en_tablero(movimiento, tablero, origen, destino) == True


    assert tablero == [
        [1, 0, 3],
        [0, 0, 0],
        [0, 0, 1]
    ]

def test_out_of_bounds():
    tablero = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    origen = (0, 0)
    destino = (0, 2)
    movimiento = Movimiento7()

    assert swapear_en_tablero(movimiento, tablero, origen, destino) == False
    assert tablero == [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
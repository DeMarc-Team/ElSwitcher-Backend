from figuras import UP, DOWN, LEFT, RIGHT, Recorrido, Figura, Figura01, hallar_todas_las_figuras_en_tablero

def test_recorrido_build_coord_set():
    recorrido = Recorrido([UP, RIGHT, DOWN, LEFT])
    coord_set = recorrido.build_coord_set((2, 2), 0, 5, 5)
    assert coord_set == {(2, 2), (1, 2), (1, 3), (2, 3), (2, 2)}

def test_figura_check_perimeter():
    figura = Figura()
    tablero = [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ]
    fig_coords_set = {(1, 1)}
    assert figura.check_perimeter(tablero, fig_coords_set, 0) == True

def test_figura_check_rotation_at():
    figura = Figura01() # T
    tablero = [
        [0, 0, 0, 1],
        [1, 0, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 1, 1]
    ]
    result = figura.check_rotation_at(tablero, (0, 0), 1, 0)
    assert result == [{(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)}]

def test_figura_check_rotation_at_should_not_match():
    figura = Figura01()
    tablero = [
        [0, 0, 0, 0],
        [1, 0, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 1, 1]
    ]
    result = figura.check_match_at(tablero, (1, 1), 0)
    assert result == []

def test_figura_matchear_en_tablero():
    figura = Figura01()
    tablero = [
        [0, 0, 0, 1],
        [1, 0, 1, 1],
        [1, 0, 1, 1],
        [1, 1, 1, 1]
    ]
    result = figura.matchear_en_tablero(tablero)
    assert result == [{(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)}]

def test_hallar_todas_las_figuras_en_tablero():
    tablero = [
        [0, 0, 0, 1, 1, 1],
        [1, 0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 2, 2, 2],
        [1, 1, 2, 2, 1, 1],

    ]
    result = hallar_todas_las_figuras_en_tablero(tablero)
    assert result['f1'] == [{(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)}]
    assert result['f3'] == [{(5, 2), (5, 3), (4, 3), (4, 4), (4, 5)}]
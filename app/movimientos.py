

class VectorMovimiento():
    """
        Indica la forma en que se puede realizar
        un movimiento en el tablero.
    """
    def __init__(self,direccion=(0,0)) -> None:
        self.direccion = direccion # Este vector indica la dirección en la que se puede mover la ficha


    def rotacion(self,n_rots=0):
        """
            Rota el vector de movimiento n_rots veces
            en sentido horario.
        """
        vec_direccion = self.direccion
        match n_rots % 4:
            case 0: 
                x,y = (vec_direccion[0],vec_direccion[1])
            case 1: # 90deg
                x,y = (vec_direccion[1],-vec_direccion[0])
            case 2: # 180deg
                x,y = (-vec_direccion[0],-vec_direccion[1])
            case 3: # 270deg
                x,y = (-vec_direccion[1],vec_direccion[0])

        return x,y

class Movimiento:
    def __init__(self) -> None:
        self.movimiento = "Pensar es el diálogo del alma consigo misma"
        self.vector_movimiento = VectorMovimiento()
        self.parcialmente_usada = False # Quiza no haga falta, pero tiene sentido

class Movimiento1(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm1'
        self.vector_movimiento = VectorMovimiento((-2,2))

class Movimiento2(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm2'
        self.vector_movimiento = VectorMovimiento((-2,0))

class Movimiento3(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm3'
        self.vector_movimiento = VectorMovimiento((-1,0))


class Movimiento4(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm4'
        self.vector_movimiento = VectorMovimiento((-1,-1))

class Movimiento5(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm5'
        self.vector_movimiento = VectorMovimiento((1,-2))

class Movimiento6(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm6'
        self.vector_movimiento = VectorMovimiento((2,1))


class Movimiento7(Movimiento):
    def __init__(self) -> None:
        super().__init__()
        self.movimiento = 'm7'
        self.vector_movimiento = VectorMovimiento((-4,0))


SET_DE_MOVIMIENTOS = [Movimiento1(),Movimiento2(),Movimiento3(),Movimiento4(),Movimiento5(),Movimiento6(),Movimiento7()]


def swapear_en_tablero(movimiento: Movimiento,tablero: list[list[int]],origen:tuple[int,int],destino:tuple[int,int]):
    """
        Realiza el movimiento indicado en el tablero SOLO si el movimiento
        es valido.

        returns: True si el movimiento es valido y se realizo, False en caso contrario.
    """

    for i in range(4):
        x,y = movimiento.vector_movimiento.rotacion(i)
        if is_valid_move(origen, destino, x, y):
            apply_swap(tablero, origen, destino)

            return True
    
    return False

def is_valid_move(origen, destino, x, y):
    matches = origen[0]+x == destino[0] and origen[1]+y == destino[1]
    dest_in_bounds = 0 <= destino[0] < 6 and 0 <= destino[1] < 6
    origin_in_bounds = 0 <= origen[0] < 6 and 0 <= origen[1] < 6

    return matches and dest_in_bounds and origin_in_bounds

def apply_swap(tablero, origen, destino):
    origin_val = tablero[origen[0]][origen[1]]
    dest_val = tablero[destino[0]][destino[1]]

    tablero[origen[0]][origen[1]] = dest_val
    tablero[destino[0]][destino[1]] = origin_val
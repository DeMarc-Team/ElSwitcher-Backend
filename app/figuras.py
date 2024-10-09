from enum import Enum

UP = (-1,0)
DOWN = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)

class Recorrido():
    def __init__(self,recorrido=[]):
        self.recorrido = recorrido

    def build_coord_set(self,initial_point = (0,0),rotated_times=0,mat_size_N=6,mat_size_M=6):
        coord_set = set()
        x,y = initial_point
        coord_set.add((x,y))
        for i in self.recorrido:
            match rotated_times % 4:
                case 0:
                    x,y = (x+i[0],y+i[1])
                case 1:
                    x,y = (x+i[1],y-i[0])
                case 2:
                    x,y = (x-i[0],y-i[1])
                case 3:
                    x,y = (x-i[1],y+i[0])
            
            if x < 0 or y < 0 or x >= mat_size_N or y >= mat_size_M:
                return {}
            
            coord_set.add((x,y))
        return coord_set

class Figura():
    """
        Figura
    """
    def __init__(self):
        self.recorrido = Recorrido()
        self.id = 'Si estas viendo esto, el back esta en problemas'

    def check_perimeter(self,tablero,fig_coords_set,matching_color):
        
        for i,j in fig_coords_set:
            for x,y in [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]:
                if (x,y) in fig_coords_set:
                    continue
                if x < 0 or y < 0 or x >= len(tablero) or y >= len(tablero[0]):
                    continue
                if tablero[x][y] == matching_color: # Hay algo en el perimetro que rompe la figura
                    return False
                

        return True

    
    def check_rotation_at(self,tablero,origen,n_rots,matching_color):
        
        N = len(tablero)
        M = len(tablero[0])

        fig_coords_set = self.recorrido.build_coord_set(origen,n_rots,N,M)

        result = []

        if fig_coords_set == {}: # Quiere decir que es imposible colocar la figura en ese origen
            return result
        
        for i,j in fig_coords_set:
            if tablero[i][j] != matching_color:
                return result
        
        if self.check_perimeter(tablero,fig_coords_set,matching_color):
            result.append(fig_coords_set)

        return result



    def check_match_at(self,tablero,origen,matching_color):
        """Chequea que la figura se puedae matchear en el tablero
            en ese origen.

        Args:
            tablero (List[List]): tablero donde chequear

            origen (tuple): tupla de coordenadas (x,y) que indican el origen

            matching_color (Object): color a matchear
        """
        
        for rot in range(4):
            find = self.check_rotation_at(tablero,origen,rot,matching_color)

            if find != []:
                return find

        # Else: no halle match con ninguna rotacion
        return []

    def matchear_en_tablero(self,tablero):
        result = []
        for i in range(len(tablero)):
            for j in range(len(tablero[i])):
                matching_color = tablero[i][j]
                result += self.check_match_at(tablero,(i,j),matching_color)
            
        return result

    
class Figura01(Figura):
    """
    Define un camino a través de una matriz para matchear la figura
    *
    ***
    * <--- Punto inicial
    """
    def __init__(self):
        self.recorrido = Recorrido([UP,UP,DOWN,RIGHT,RIGHT])
        self.id = 'f1'

class Figura02(Figura):
    """               OO 
        Figura snake:  OOO
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,DOWN,RIGHT,RIGHT])
        self.id = 'f2'

class Figura03(Figura):
    """              OO
        Otra snake OOO
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP,RIGHT])
        self.id = 'f3'

class Figura04(Figura):
    """         O
       Escalera:OO
                 OO
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([DOWN,RIGHT,DOWN,RIGHT])
        self.id = 'f4'
    

def hallar_todas_las_figuras_en_tablero(tablero):
    """Ecuentra todas las las figuras en el tablero dado un set de colores

    Args:
        tablero (List[List]): Matriz NxM
        colores (Any): Cualquier cosa que represente un color

    Returns:
        List[Set{tuplas}]: Lista de sets de tuplas. Cada set representa una figura, y las tuplas de cada set las coordenadas de una figura
    """
    figuras = [Figura01(),Figura02(),Figura03(),Figura04()]
    result = {}
    for figura in figuras:
        result[figura.id] = figura.matchear_en_tablero(tablero)


    return result
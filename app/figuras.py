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
        self.es_dificil = True

class Figura02(Figura):
    """               OO 
        Figura snake:  OOO
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,DOWN,RIGHT,RIGHT])
        self.id = 'f2'
        self.es_dificil = True

class Figura03(Figura):
    """              OO
        Otra snake OOO
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP,RIGHT])
        self.id = 'f3'
        self.es_dificil = True

class Figura04(Figura):
    """         O
       Escalera:OO
                 OO
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([DOWN,RIGHT,DOWN,RIGHT])
        self.id = 'f4'
        self.es_dificil = True

class Figura05(Figura):
    """ 
    linea: 00000
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,RIGHT,RIGHT])
        self.id = 'f5'
        self.es_dificil = True

class Figura06(Figura):
    """ 
    L : 0
        0
        000
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([DOWN,DOWN,RIGHT,RIGHT])
        self.id = 'f6' 
        self.es_dificil = True

class Figura07(Figura):
    """ 
    L invertida larga: 0000
                          0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,RIGHT,DOWN])
        self.id = 'f7' 
        self.es_dificil = True

class Figura08(Figura):
    """ 
                0
    L larga: 0000
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,RIGHT,UP])
        self.id = 'f8' 
        self.es_dificil = True

class Figura09(Figura):
    """ 
                 0
    Silla   : 0000
               0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,DOWN,UP,RIGHT,UP])
        self.id = 'f9'
        self.es_dificil = True

class Figura10(Figura):
    """ 
                0
    OLEEE   : 000
              0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([UP,RIGHT,RIGHT,UP])
        self.id = 'f10'
        self.es_dificil = True

class Figura11(Figura):
    """ 
                     0
    silla_invertida: 000
                      0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([LEFT,DOWN,UP,LEFT,UP])
        self.id = 'f11'
        self.es_dificil = True

class Figura12(Figura):
    """ 
              0
    OZOOO   : 000
                0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([DOWN,RIGHT,RIGHT,DOWN])
        self.id = 'f12'
        self.es_dificil = True

class Figura13(Figura):
    """ 
             
    Porra: 0000
             0
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,DOWN,UP,RIGHT])
        self.id = 'f13'
        self.es_dificil = True

class Figura14(Figura):
    """ 
              0
    Porra2: 0000
             
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP,DOWN,RIGHT])
        self.id = 'f14'
        self.es_dificil = True

class Figura15(Figura):
    """ 
              00
    caracol: 000
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP,LEFT])
        self.id = 'f15'
        self.es_dificil = True

class Figura16(Figura):
    """ 
            0 0
    cuenco: 000
                 
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP,LEFT])
        self.id = 'f16'
        self.es_dificil = True

class Figura17(Figura):
    """ 
          0
    cruz 000
          0      
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,UP,DOWN,DOWN,UP,RIGHT])
        self.id = 'f17'
        self.es_dificil = True

class Figura18(Figura):
    """ 

    cracol en acido: 000
                      00     
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,DOWN,LEFT])
        self.id = 'f18'
        self.es_dificil = True
    
class Figura19(Figura):
    """ 
               00
    escalon : 00
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,UP,RIGHT])
        self.id = 'f19'
        self.es_dificil = False

class Figura20(Figura):
    """ 
               00
    cuadrao  : 00
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,UP,LEFT])
        self.id = 'f20'
        self.es_dificil = False

class Figura21(Figura):
    """ 
                     00
    escalon patras  : 00
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,DOWN,RIGHT])
        self.id = 'f21'
        self.es_dificil = False

class Figura22(Figura):
    """ 
                       0
    arrow keys      : 000
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,UP,DOWN,RIGHT])
        self.id = 'f22'
        self.es_dificil = False

class Figura23(Figura):
    """ 
     
    L invertida: 000
                   0
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,DOWN])
        self.id = 'f23'
        self.es_dificil = False

class Figura24(Figura):
    """ 
     
    Palo: 0000
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,RIGHT])
        self.id = 'f24'
        self.es_dificil = False

class Figura25(Figura):
    """ 
          0
    L : 000
                           
    """
    def __init__(self):
        self.recorrido = Recorrido([RIGHT,RIGHT,UP])
        self.id = 'f25'
        self.es_dificil = False


# Dios me perdone por esto (Copilot autocompletó este mensaje jasklda)
SET_DE_CARTAS = [Figura01(),Figura02(),Figura03(),Figura04(),Figura05(),Figura06(),Figura07(),Figura08(),Figura09(),Figura10(),Figura11(),Figura12(),Figura13(),Figura14(),Figura15(),Figura16(),Figura17(),Figura18(),Figura19(),Figura20(),Figura21(),Figura22(),Figura23(),Figura24(),Figura25()]
SET_DE_CARTAS_FACILES = [i for i in SET_DE_CARTAS if i.es_dificil == False]
SET_DE_CARTAS_DIFICILES = [i for i in SET_DE_CARTAS if i.es_dificil == True]

    

def hallar_todas_las_figuras_en_tablero(tablero):
    """Ecuentra todas las las figuras en el tablero dado un set de colores

    Args:
        tablero (List[List]): Matriz NxM
        colores (Any): Cualquier cosa que represente un color

    Returns:
        List[Set{tuplas}]: Lista de sets de tuplas. Cada set representa una figura, y las tuplas de cada set las coordenadas de una figura
    """
    figuras = SET_DE_CARTAS
    result = {}
    for figura in figuras:
        matches_para_figura = figura.matchear_en_tablero(tablero)
        if matches_para_figura != []:
            result[figura.id] = matches_para_figura


    return result

class MazoDeCartasFigura():
    def __init__(self):
        """Como dice el reglamento
           hay cuatro sets del mismo mazo
           de figuras y se reparte un mazo para cada jugador
        """
        self.cartas = 4*SET_DE_CARTAS # Cuatro juegos.


    def repartir_para_n(self, n_jugadores: int):
        """
        Reparte el mazo de cartas de figura para n jugadores
        Args:
            n_jugadores (int): cantidad de jugadores

        Returns:
            List[List[Figura]]: Lista de listas de figuras
        """        
        # TODO: Abrir el ticket para hacer esto
        pass
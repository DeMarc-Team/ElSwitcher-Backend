from sqlalchemy.orm import Session
from models import Partida, Jugador


def crear_partida(db: Session, nombre_partida: str = "Partida", nombre_creador: str = "Creador") -> Partida:
    '''
    Función para crear una partida
    Devuelve la partida creada y el jugador creador
    Valores por defecto:
    - nombre_partida = Partida
    - nombre_creador = Creador
    - tablero = '[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'
    '''
    nueva_partida = Partida(nombre_partida=nombre_partida,
                            nombre_creador=nombre_creador,
                            iniciada=False,
                            tablero='[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]')
    creador = Jugador(nombre=nombre_creador,
                      partida=nueva_partida,
                      es_creador=True,
                      orden=0)
    nueva_partida.jugadores.append(creador)
    
    db.add(creador)
    db.add(nueva_partida)
    db.commit()

    return nueva_partida, creador


def unir_jugadores(db: Session, partida: Partida = "Partida", numero_de_jugadores: int = 1) -> Jugador:
    '''
    Función para unir jugadores a una partida
    Devuelve el jugador creado
    Valores por defecto:
    - partida = Partida
    - numero_de_jugadores = 1
    - nombre = Jugador{i} donde i va desde 2 hasta 4
    '''
    assert partida.iniciada == False, "La partida ya ha sido iniciada"
    assert len(partida.jugadores) <= 4, "La partida ya tiene 4 jugadores"
    assert numero_de_jugadores < 4, "No se pueden unir más de 4 jugadores a la partida"
    assert numero_de_jugadores > 0, "Y el creador? boludito"

    for i in range(numero_de_jugadores):
        nuevo_jugador = Jugador(nombre=f"Jugador{i+2}", partida=partida, es_creador=False, orden=len(partida.jugadores))
        db.add(nuevo_jugador)
        partida.jugadores.append(nuevo_jugador)
        db.commit()

    return nuevo_jugador

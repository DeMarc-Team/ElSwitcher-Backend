from sqlalchemy.orm import Session
import mock
from models import (Partida,
                    Jugador,
                    CartaFigura,
                    CartaMovimiento
                    )


def crear_partida(db: Session, nombre_partida: str = "Partida", nombre_creador: str = "Creador") -> Partida:
    '''
    Función para crear una partida.

    Devuelve la partida creada y el jugador creador.

    Valores por defecto:
    - nombre_partida = Partida
    - nombre_creador = Creador
    - iniciada = False
    - tablero = '[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]'
    '''
    partida = Partida(nombre_partida=nombre_partida,
                            nombre_creador=nombre_creador,
                            iniciada=False,
                            tablero='[[2, 1, 3, 4, 2, 3], [4, 2, 1, 1, 3, 3], [2, 1, 3, 2, 3, 4], [4, 1, 1, 2, 2, 4], [1, 3, 1, 2, 1, 3], [2, 3, 4, 4, 4, 4]]')
    creador = Jugador(nombre=nombre_creador,
                      partidas=partida,
                      es_creador=True,
                      orden=0)
    partida.jugadores.append(creador)
    
    db.add(creador)
    db.add(partida)

    db.commit()
    return partida, creador


def unir_jugadores(db: Session, partida: Partida , numero_de_jugadores: int = 1) -> Jugador:
    '''
    Función para unir jugadores a una partida.

    Devuelve una lista con los jugadores unidos a la partida.

    Valores por defecto:
    - partida = Partida
    - numero_de_jugadores = 1
    - nombre = Jugador{i} donde i va desde 2 hasta 4
    '''
    assert partida.iniciada == False, "La partida ya ha sido iniciada"
    assert len(partida.jugadores) <= 4, "La partida ya tiene 4 jugadores"
    assert numero_de_jugadores < 4, "No se pueden unir más de 4 jugadores a la partida"
    assert numero_de_jugadores > 0, "Y el creador? boludito"

    nuevos_jugadores = []
    for i in range(numero_de_jugadores):
        nuevo_jugador = Jugador(nombre=f"Jugador{i+2}", partidas=partida, es_creador=False, orden=len(partida.jugadores))
        db.add(nuevo_jugador)
        partida.jugadores.append(nuevo_jugador)
        nuevos_jugadores.append(nuevo_jugador)
        db.commit()

    db.commit()
    return nuevos_jugadores

def iniciar_partida(db: Session, partida: Partida) -> Partida:
    '''
    Función para iniciar una partida.

    Devuelve la partida iniciada.
    '''
    assert partida.iniciada == False, "La partida ya ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder iniciarla"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    partida.iniciada = True

    repartir_cartas_figura(db, partida)
    repartir_cartas_movimiento(db, partida)

    db.commit()
    return partida

def repartir_cartas_figura(db: Session, partida: Partida):
    '''
    Función para repartir las cartas de figura a los jugadores de una partida.
    '''
    assert partida.iniciada == True, "La partida no ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder repartir las cartas de figura"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    # Crear las cartas de figura
    for jugador in partida.jugadores:
        for i in range(3):
            carta = CartaFigura(poseida_por=jugador)
            db.add(carta)

    db.commit()
    return partida

def repartir_cartas_movimiento(db: Session, partida: Partida):
    '''
    Función para repartir las cartas de figura a los jugadores de una partida.
    '''
    assert partida.iniciada == True, "La partida no ha sido iniciada"
    assert len(partida.jugadores) > 1, "La partida debe tener al menos 2 jugadores para poder repartir las cartas de figura"
    assert len(partida.jugadores) <= 4, "La partida no puede tener más de 4 jugadores"

    # Crear las cartas de figura
    for jugador in partida.jugadores:
        for i in range(3):
            carta = CartaMovimiento(movimientos_de=jugador)
            db.add(carta)
            
def abandonar_partida(db: Session, partida: Partida, jugador: Jugador) -> Partida:
    '''
    Función para abandonar una partida.

    Devuelve la partida actualizada.
    '''
    assert not (not partida.iniciada and jugador.es_creador), "El creador no puede abandonar la partida antes de iniciarla"

    partida = db.query(Partida).filter(Partida.id == partida.id).first()
    
    partida.jugadores.remove(jugador)
    db.delete(jugador)
    db.flush()

    if (len(partida.jugadores) == 1):
        db.delete(partida)    

    db.commit()
    return partida
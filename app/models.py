from database import Base

from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.orderinglist import ordering_list

# JUGADOR ------------------------------------------------------
class Jugador(Base):
    __tablename__ = 'jugadores'
    id_jugador: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255))
    es_creador: Mapped[Boolean] = mapped_column(Boolean, default=False)
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'))
    partidas = relationship("Partida", back_populates="jugadores")

    juego_id: Mapped[int] = mapped_column(Integer, ForeignKey('juegos.id'), nullable=True)
    juegos: Mapped[list['Juego']] = relationship("Juego", back_populates="jugadores")
    
    orden: Mapped[int] = mapped_column(Integer, nullable=True)
    mazo_cartas_de_figura:Mapped[list['CartaFigura']] = relationship('CartaFigura', back_populates='poseida_por')
    mano_movimientos: Mapped[list['CartaMovimiento']] = relationship('CartaMovimiento', back_populates='movimientos_de')

# PARTIDA ------------------------------------------------------
class Partida(Base):
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_partida = mapped_column(String(255))
    nombre_creador = mapped_column(String(200))
    iniciada = mapped_column(Boolean, default=False)

    jugadores: Mapped[list[Jugador]] = relationship('Jugador', back_populates='partidas')
    juego = relationship('Juego', back_populates='partida')

    @hybrid_property # TODO: Revisar el cambio de que pueda no haber un creador si la partida está iniciada
    def id_creador(self) -> int:
        jugador_creador = next((jugador for jugador in self.jugadores if jugador.es_creador), None)
        if jugador_creador is not None:
            return jugador_creador.id_jugador
        if self.iniciada == False:
            raise Exception('No se encontró el jugador creador')

# JUEGO --------------------------------------------------------
def random_tablero():
    """Genera una lista de 36 fichas de 4 colores distintos mezcladas aleatoriamente
    Returns:
        String: Lista de fichas (Como JSON)
    """
    from random import shuffle
    import json
    set_de_fichas = [1 for i in range(9) ] + [2 for i in range(9) ] + [3 for i in range(9) ] + [4 for i in range(9) ] # 36 fichas de 4 colores distintos
    shuffle(set_de_fichas) # Mezclar las fichas
    tablero = []
    for i in range(6):
        tablero.append(set_de_fichas[i*6:i*6+6])  # Agregar de a 6 las casillas del set mezclado

    tablero_as_json = json.dumps(tablero)

    return tablero_as_json


class Juego(Base):
    __tablename__ = 'juegos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    jugadores: Mapped[list[Jugador]] = relationship('Jugador', order_by='Jugador.orden',
                                                    collection_class=ordering_list('orden'))
    
    @hybrid_property
    def jugador_del_turno(self) -> Jugador:
        if self.partida and self.partida.jugadores:
            return self.jugadores[0]  # Retorna el jugador en la primera posición
        return None
    
    @hybrid_property
    def jugador_id(self) -> int:
        if self.partida and self.partida.jugadores:
            return self.jugadores[0].id_jugador  # Retorna el jugador en la primera posición
        return None
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'), unique=True)
    partida: Mapped[Partida] = relationship('Partida', back_populates='juego')

    tablero = mapped_column(String, nullable=False, default=random_tablero())

# CartaFigura --------------------------------------------------

class CartaFigura(Base):

    __tablename__ = 'cartas_de_figura'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    def random_figura():
        import random
        return random.choice(['f1','f2','f3'])
    
    figura: Mapped[str] = mapped_column(String, nullable=False, default=lambda: CartaFigura.random_figura())
    revelada: Mapped[Boolean] = mapped_column(Boolean, default=True) # Default true para que en la demo se vea ajsja

    poseida_por = relationship('Jugador', back_populates='mazo_cartas_de_figura') # Las relaciones necesitan que exista además una foreign key
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))
    
# CartaMovimiento --------------------------------------------------
class CartaMovimiento(Base):

    __tablename__ = 'cartas_de_movimiento'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    
    def random_movimiento():
        import random
        return random.choice(['m1', 'm2', 'm3'])
    
    movimiento: Mapped[str] = mapped_column(String, nullable=False, default=lambda: CartaMovimiento.random_movimiento())

    movimientos_de = relationship('Jugador', back_populates='mano_movimientos') # Las relaciones necesitan que exista además una foreign key
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))
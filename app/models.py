from database import Base

from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column


# JUGADOR ------------------------------------------------------
class Jugador(Base):
    __tablename__ = 'jugadores'
    id_jugador: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255))
    es_creador: Mapped[Boolean] = mapped_column(Boolean, default=False)
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'))
    partidas = relationship("Partida", back_populates="jugadores")

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

    @hybrid_property
    def id_creador(self) -> int:
        jugador_creador = next((jugador for jugador in self.jugadores if jugador.es_creador), None)
        if jugador_creador is not None:
            return jugador_creador.id_jugador
        raise Exception('No se encontró el jugador creador')

# JUEGO --------------------------------------------------------
class Juego(Base):
    __tablename__ = 'juegos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    jugador_id: Mapped[int] =  mapped_column(Integer, ForeignKey('jugadores.id_jugador'), unique=True)
    jugador_del_turno: Mapped[Jugador] = relationship('Jugador')
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'), unique=True)
    partida: Mapped[Partida] = relationship('Partida', back_populates='juego')


# CartaFigura --------------------------------------------------

def random_figura(): # TODO: No supe poner esto como metodo de la clase CartaFigura pero quedaria mejor
    import random
    return random.choice(['f1','f2','f3'])

class CartaFigura(Base):

    __tablename__ = 'cartas_de_figura'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    figura: Mapped[str] = mapped_column(String, nullable=False, default = random_figura())

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
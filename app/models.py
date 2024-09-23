from database import Base

from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


# JUGADOR ------------------------------------------------------
class Jugador(Base):
    __tablename__ = 'jugadores'
    id_jugador: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255))
    es_creador: Mapped[Boolean] = mapped_column(Boolean, default=False)
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'))
    partidas = relationship("Partida", back_populates="jugadores")

# PARTIDA ------------------------------------------------------
class Partida(Base):
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_partida = mapped_column(String(255))
    nombre_creador = mapped_column(String(200))
    iniciada = mapped_column(Boolean, default=False)

    jugadores: Mapped[list[Jugador]] = relationship('Jugador', back_populates='partidas')
    juego = relationship('Juego', back_populates='partida')

# JUEGO --------------------------------------------------------
class Juego(Base):
    __tablename__ = 'juegos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    turno: Mapped[int] =  mapped_column(Integer, ForeignKey('jugadores.id_jugador'))
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'), unique=True)
    partida: Mapped[Partida] = relationship('Partida', back_populates='juego')
    
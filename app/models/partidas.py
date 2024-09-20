from database import Base
from models.jugadores import Jugador
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Partida(Base):
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_partida = mapped_column(String(255))
    nombre_creador = mapped_column(String(200))
    iniciada = mapped_column(Boolean)

    jugadores: Mapped[list[Jugador]] = relationship('Jugador', back_populates='partidas')
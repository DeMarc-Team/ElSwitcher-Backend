from app.database import Base

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

class Jugador(Base):
    __tablename__ = 'jugadores'
    id_jugador: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255))
    
    partida_id: Mapped[int] = mapped_column(Integer, ForeignKey('partidas.id'))
    partidas = relationship("Partida", back_populates="jugadores")
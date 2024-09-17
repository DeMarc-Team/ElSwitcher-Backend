from database import Base
from sqlalchemy import Enum as Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

class Partida(Base):
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = mapped_column(String(255))
    iniciada = mapped_column(Boolean)
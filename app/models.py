from database import Base

from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.orderinglist import ordering_list

# JUGADOR ------------------------------------------------------


class Jugador(Base):
    __tablename__ = 'jugadores'
    id_jugador: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    es_creador: Mapped[Boolean] = mapped_column(Boolean, default=False)

    partida_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('partidas.id'), nullable=False)
    partidas = relationship("Partida", back_populates="jugadores")

    orden: Mapped[int] = mapped_column(Integer, nullable=True)
    mazo_cartas_de_figura: Mapped[list['CartaFigura']] = relationship(
        'CartaFigura', back_populates='poseida_por', cascade="all, delete-orphan")
    mano_movimientos: Mapped[list['CartaMovimiento']] = relationship(
        'CartaMovimiento', back_populates='movimientos_de', cascade="all, delete-orphan")

    def __repr__(self):  # pragma: no cover
        return (f"<Jugador(id_jugador={self.id_jugador}, nombre='{self.nombre}', "
                f"es_creador={self.es_creador}, partida_id={self.partida_id}, orden={self.orden})>")
# PARTIDA ------------------------------------------------------


def random_tablero():
    """Genera una lista de 36 fichas de 4 colores distintos mezcladas aleatoriamente
    Returns:
        String: Lista de fichas (Como JSON)
    """
    from random import shuffle
    import json
    set_de_fichas = [1 for i in range(9)] + [2 for i in range(9)] + [3 for i in range(9)] + [
        4 for i in range(9)]  # 36 fichas de 4 colores distintos
    shuffle(set_de_fichas)  # Mezclar las fichas
    tablero = []
    for i in range(6):
        # Agregar de a 6 las casillas del set mezclado
        tablero.append(set_de_fichas[i*6:i*6+6])

    tablero_as_json = json.dumps(tablero)

    return tablero_as_json


class Partida(Base):
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)
    nombre_partida = mapped_column(String(255), nullable=False)
    nombre_creador = mapped_column(String(200), nullable=False)
    iniciada = mapped_column(Boolean, default=False)

    jugadores: Mapped[list[Jugador]] = relationship('Jugador', order_by='Jugador.orden',
                                                    collection_class=ordering_list('orden'))
    
    tablero = mapped_column(String, nullable=False, default=random_tablero())

    @hybrid_property
    def jugador_del_turno(self) -> Jugador:
        if self.jugadores:
            # Retorna el jugador en la primera posición
            return self.jugadores[0]
        return None

    @hybrid_property
    def jugador_id(self) -> int:
        if self.partida and self.partida.jugadores:
            # Retorna el jugador en la primera posición
            return self.jugadores[0].id_jugador
        return None

    @hybrid_property
    def id_creador(self) -> int:
        jugador_creador = next(
            (jugador for jugador in self.jugadores if jugador.es_creador), None)
        if jugador_creador is not None:
            return jugador_creador.id_jugador

        if self.iniciada == False:
            raise Exception('No se encontró el jugador creador')

    def __repr__(self):  # pragma: no cover
        return (f"<Partida(id={self.id}, nombre_partida='{self.nombre_partida}', "
                f"nombre_creador='{self.nombre_creador}', iniciada={
                    self.iniciada}, "
                f"jugadores_count={len(self.jugadores)})>")




# CartaFigura --------------------------------------------------

class CartaFigura(Base):

    __tablename__ = 'cartas_de_figura'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)

    def random_figura():
        import random
        return random.choice(['f1', 'f2', 'f3'])

    figura: Mapped[str] = mapped_column(
        String, nullable=False, default=lambda: CartaFigura.random_figura())
    # Default true para que en la demo se vea ajsja
    revelada: Mapped[Boolean] = mapped_column(Boolean, default=True)

    # Las relaciones necesitan que exista además una foreign key
    poseida_por = relationship(
        'Jugador', back_populates='mazo_cartas_de_figura')
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))

    def __repr__(self):  # pragma: no cover
        return (f"<CartaFigura(id={self.id}, figura='{self.figura}', "
                f"revelada={self.revelada}, jugador_id={self.jugador_id})>")

# CartaMovimiento --------------------------------------------------


class CartaMovimiento(Base):

    __tablename__ = 'cartas_de_movimiento'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)

    def random_movimiento():
        import random
        return random.choice(['m1', 'm2', 'm3'])

    movimiento: Mapped[str] = mapped_column(
        String, nullable=False, default=lambda: CartaMovimiento.random_movimiento())

    # Las relaciones necesitan que exista además una foreign key
    movimientos_de = relationship('Jugador', back_populates='mano_movimientos')
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))

    def __repr__(self):  # pragma: no cover
        return (f"<CartaMovimiento(id={self.id}, movimiento='{self.movimiento}', "
                f"jugador_id={self.jugador_id})>")

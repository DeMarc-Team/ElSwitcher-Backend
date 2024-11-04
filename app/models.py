from database import Base
from exceptions import ResourceNotFoundError

from sqlalchemy import Integer, Boolean, String, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.orderinglist import ordering_list
from figuras import SET_DE_CARTAS

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
    bloqueado: Mapped[Boolean] = mapped_column(Boolean, default=False)
    
    @hybrid_property
    def numero_de_cartas_figura(self) -> int:
        return len(self.mazo_cartas_de_figura)

    @hybrid_property
    def id(self) -> int:
        return self.id_jugador
    
    @hybrid_property
    def mano_figuras(self) -> list['CartaFigura']:
        return [carta for carta in self.mazo_cartas_de_figura if carta.revelada]
        
    def __str__(self):  # pragma: no cover
        return (f"<Jugador(id_jugador={self.id_jugador}, nombre={self.nombre}, "
                f"es_creador={self.es_creador}, partida_id={self.partida_id}, orden={self.orden}, "
                f"numero_de_cartas_figura={len(self.mazo_cartas_de_figura)}, "
                f"numero_de_cartas_movimiento={len(self.mano_movimientos)})>")
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
    # PARTIDA -----------------------
    __tablename__ = 'partidas'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)
    nombre_partida = mapped_column(String(255), nullable=False)
    nombre_creador = mapped_column(String(200), nullable=False)
    iniciada = mapped_column(Boolean, default=False)
    jugadores: Mapped[list[Jugador]] = relationship(
        'Jugador', back_populates='partidas', cascade="all", order_by='Jugador.orden', collection_class=ordering_list('orden'))
    
    @hybrid_property
    def numero_de_jugadores(self) -> int:
        return len(self.jugadores)
    
    @hybrid_property
    def id_creador(self) -> int:
        id_jugador_creador = next(
            (jugador.id_jugador for jugador in self.jugadores if jugador.es_creador), None)
        if id_jugador_creador is not None or self.iniciada:
            return id_jugador_creador
        if self.iniciada == False:
            raise Exception('No se encontró el jugador creador')
    
    # JUEGO -----------------------
    @hybrid_property
    def jugador_del_turno(self) -> Jugador:
        # Retorna el jugador en la primera posición
        return self.jugadores[0]

    @hybrid_property
    def jugador_id(self) -> int: # FIXME: Sacar y usar partida.jugador_del_turno.id_jugador
        # Retorna el jugador en la primera posición
        return self.jugadores[0].id_jugador

    inicio_turno = mapped_column(String, nullable=False, default='0')
    duracion_turno = mapped_column(Integer, nullable=False, default=0)
    tablero = mapped_column(String, nullable=False, default=random_tablero)

    movimientos_parciales = relationship('MovimientoParcial', order_by='MovimientoParcial.orden')

    def __str__(self):  # pragma: no cover
        return (f"<Partida(id={self.id}, nombre_partida='{self.nombre_partida}', "
            f"nombre_creador='{self.nombre_creador}', iniciada={self.iniciada}, "
            f"numero_de_jugadores={len(self.jugadores)}, tablero='{self.tablero}')>")

# CartaFigura --------------------------------------------------

class CartaFigura(Base):

    __tablename__ = 'cartas_de_figura'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)

    def random_figura():
        import random
        # FIXME: En realidad deberían salir cartas acorde a las que el jugador nunca tuvo
        return random.choice(SET_DE_CARTAS).id

    figura: Mapped[str] = mapped_column(
        String, nullable=False, default=lambda: CartaFigura.random_figura())
    revelada: Mapped[Boolean] = mapped_column(Boolean, default=True)
    bloqueada: Mapped[Boolean] = mapped_column(Boolean, default=False)

    # Las relaciones necesitan que exista además una foreign key
    poseida_por = relationship(
        'Jugador', back_populates='mazo_cartas_de_figura')
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))

    def __str__(self):  # pragma: no cover
        return (f"<CartaFigura(id={self.id}, figura='{self.figura}', "
                f"revelada={self.revelada}, jugador_id={self.jugador_id})>")

# CartaMovimiento --------------------------------------------------


class CartaMovimiento(Base):

    __tablename__ = 'cartas_de_movimiento'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)

    def random_movimiento():
        import random
        from movimientos import SET_DE_MOVIMIENTOS
        return random.choice([carta_mov.movimiento for carta_mov in SET_DE_MOVIMIENTOS])

    movimiento: Mapped[str] = mapped_column(
        String, nullable=False, default=lambda: CartaMovimiento.random_movimiento())

    # Las relaciones necesitan que exista además una foreign key
    movimientos_de = relationship('Jugador', back_populates='mano_movimientos')
    jugador_id = mapped_column(Integer, ForeignKey('jugadores.id_jugador'))

    movimiento_parcial_en = relationship('MovimientoParcial', uselist=False, back_populates='carta', cascade="all, delete-orphan")

    @hybrid_property
    def usada_en_movimiento_parcial(self):
        return self.movimiento_parcial_en is not None

    def __str__(self):  # pragma: no cover
        return (f"<CartaMovimiento(id={self.id}, movimiento='{self.movimiento}', "
                f"jugador_id={self.jugador_id})>")

class MovimientoParcial(Base):
    __tablename__ = 'movimientos_parciales'
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True)
    carta_id = mapped_column(Integer, ForeignKey('cartas_de_movimiento.id'))
    carta = relationship('CartaMovimiento')
    
    partida_id = mapped_column(Integer, ForeignKey('partidas.id'))

    origen: Mapped[tuple[int, int]] = mapped_column(String, nullable=False)
    destino: Mapped[tuple[int, int]] = mapped_column(String, nullable=False)
    
    orden = mapped_column(Integer, nullable=False)

    @hybrid_property
    def movimiento(self):
        return self.carta.movimiento

    def __str__(self):  # pragma: no cover
        return (f"<JugadaParcial(id={self.id}, carta_id={self.carta_id}, "
                f"origen={self.origen}, destino={self.destino}, partida_id={self.partida_id})>")
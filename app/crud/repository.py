from database import engine, get_db, localSession
from exceptions import ResourceNotFoundError, ForbiddenError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Partida, Jugador, CartaFigura, CartaMovimiento
import os

_engine = engine
session = localSession()

class BaseRepository():
    """
        Todos los metodos que deberian ser generales entre
        los modelos
    """
    session: Session = session
    model = None

    @classmethod
    def delete(cls, delete_me: Partida) -> None:

        if not delete_me:
            raise ResourceNotFoundError(f"Se intento eliminar un None de la tabla {cls.model.__tablename__}.")
        
        if not cls.session.query(cls.model).filter(cls.model.id == delete_me.id).first():
            raise ResourceNotFoundError(f"No se encontro ningun elemento con ID {delete_me.id} en la tabla {cls.model.__tablename__}.")

        cls.session.delete(delete_me)
        cls.session.flush()
    
    @classmethod
    def get_by_id(cls, id_to_match):
        """
            Obtener un elemento del repositorio 
            usando el id
        """
        query_result = cls.session.query(cls.model).filter(cls.model.id == id_to_match).first()
        if not query_result:
            raise ResourceNotFoundError(f"No ningun elemento con ID {id_to_match} en la tabla {cls.model.__tablename__}.")
        
        return query_result
    
    @classmethod
    def get_all(cls):
        """
            Obtener todos los elementos de este repositorio
            como una lista (resultado de query().all())
        """
        query_result = cls.session.query(cls.model).all()
    
        return query_result
    
    def commit_transactions(cls):
        """
            Hacer commit de todas las transacciones
            pendientes en la session
        """
        cls.session.commit()


class PartidaRepo(BaseRepository):
    model = Partida

    def get_jugador_del_turno(self, partida_id):
        """
            Obtener el jugador del turno actual
            de una partida
        """
        try:
            partida = self.get_by_id(partida_id)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"No se encontro ninguna partida con ID {partida_id} al buscar el jugador del turno.")
        
        return partida.jugador_del_turno
    
    def get_color_prohibido(self, partida_id):
        """
            Obtener el color prohibido de una partida
        """
        try:
            partida = self.get_by_id(partida_id)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"Partida con ID {partida_id} no encontrada.")
        
        return partida.color_prohibido

partida_repo = PartidaRepo()

class JugadoresRepo(BaseRepository):
    model = Jugador

    def get_cartas_figura(self, jugador_id):
        """
            Obtener las cartas de figura de un jugador
        """
        try:
            jugador = self.get_by_id(jugador_id)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"No se encontro ningun jugador con ID {jugador_id} al buscar sus cartas de figura.")
        
        return jugador.mazo_cartas_de_figura
    
    def get_cartas_movimiento(self, jugador_id):
        """
            Obtener las cartas de movimiento de un jugador
        """

        try:
            jugador = self.get_by_id(jugador_id)
        except ResourceNotFoundError:
            raise ResourceNotFoundError(f"No se encontro ningun jugador con ID {jugador_id} al buscar sus cartas de movimiento.")
        return jugador.mano_movimientos

class CartasFiguraRepo(BaseRepository):
    model = CartaFigura

class CartasMovimientoRepo(BaseRepository):
    model = CartaMovimiento
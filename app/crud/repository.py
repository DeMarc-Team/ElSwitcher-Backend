from database import engine, get_db, localSession
from exceptions import ResourceNotFoundError, ForbiddenError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Partida, Jugador, CartaFigura
import os

# Si el motor y la session storage estan creados por database.py, usarlos
_engine = engine
_Session = localSession()

# BaseRepository class
class BaseRepository():
    """
        Todos los metodos que deberian ser generales entre
        los modelos
    """
    session: Session = _Session
    model = None

    @classmethod
    def delete(cls, delete_me: Partida) -> None:
        cls.session.delete(delete_me)
        cls.session.flush()
    
    @classmethod
    def get_by_id(cls, id_to_match):
        """
            Obtener una partida matcheando por id
        """
        query_result = cls.session.query(cls.model).filter(cls.model.id == id_to_match).first()
        if not query_result:
            raise ResourceNotFoundError(f"Partida con ID {id_to_match} no encontrada.")
        
        return query_result
    
    @classmethod
    def get_all(cls):
        """
            Obtener la lista de partidas de la base de datos
        """
        query_result = cls.session.query(cls.model).all()
    
        return query_result

class PartidaRepo(BaseRepository):
    model = Partida

class JugadoresRepo(BaseRepository):
    model = Jugador

class CartasFiguraRepo(BaseRepository):
    model = CartaFigura

class CartasMovimientoRepo(BaseRepository):
    model = CartaFigura
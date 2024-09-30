from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

import crud.jugadores as crud
from models import Base, Jugador
from database import engine, get_db
from schemas import JugadorData, JugadorOnCreateResponse

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas"
)


@router.get('/{partida_id:int}/jugadores',
            response_model=list[JugadorOnCreateResponse],
            summary="Obtener jugadores de una partida",
            description="Devuelve la lista de jugadores que pertenecen a la partida especificada por partida_id.",
            tags=["Jugadores"])
async def get_jugadores(partida_id: int, db: Session = Depends(get_db)):
    return crud.get_jugadores(db, partida_id)


@router.post('/{partida_id:int}/jugadores',
             response_model=JugadorOnCreateResponse,
             summary="Unirse a una partida",
             description="Crea un nuevo jugador, para el usuario, en la partida especificada por partida_id.",
             tags=["Jugadores"])
async def join_to_partida(partida_id: int, jugador: JugadorData, db: Session = Depends(get_db)):
    return crud.create_jugador(db, Jugador(nombre=jugador.nombre, partida_id=partida_id))

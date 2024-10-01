from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

import crud.juego
import crud.partidas
from models import Base
from schemas import CartaFiguraData, CartaMovimientoData, TurnoDetails
from database import engine, get_db

from pydantic import Json


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/juego"
)


@router.get('/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura',
            response_model=list[CartaFiguraData],
            summary="Obtener cartas figura de un jugador",
            description="Devuelve las cartas figura de un jugador.",
            tags=["Juego"])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, db: Session = Depends(get_db)):
    return crud.partidas.get_cartas_figura_jugador(db=db, partida_id=partida_id, jugador_id=jugador_id)


@router.get('/{id_partida:int}/turno',
            response_model=TurnoDetails,
            summary="Obtener la información de quien posee el turno.",
            description="Devuelve el nombre y el identificador de quien posee el turno en una partida.",
            tags=["Juego"])
async def get_turno_details(id_partida: int,  db: Session = Depends(get_db)):
    return crud.juego.get_turno_details(db=db, partida_id=id_partida)


@router.put('/{id_partida:int}/jugadores/{id_jugador:int}/turno',
            summary="Terminar el turno del jugador actual.",
            description="Termina el turno del jugador actual, si es que el id del mismo coincide con el del parámetro.",
            tags=["Juego"])
async def terminar_turno(id_partida: int, id_jugador, db: Session = Depends(get_db)):
    return crud.juego.terminar_turno(db, id_partida, id_jugador)


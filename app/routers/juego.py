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


@router.put('/{id_partida:int}/jugadores/{id_jugador:int}/turno',
            summary="Terminar el turno del jugador actual.",
            description="Termina el turno del jugador actual, si es que el id del mismo coincide con el del parámetro.",
            tags=["Juego"])
async def terminar_turno(id_partida: int, id_jugador, db: Session = Depends(get_db)):
    return crud.juego.terminar_turno(db, id_partida, id_jugador)


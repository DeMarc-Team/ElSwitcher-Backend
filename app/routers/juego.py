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


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/juego",
    tags=["juego"]
)

@router.get('/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura',
             response_model=list[CartaFiguraData],
             summary="Obtener cartas figura de un jugador",
             description="Devuelve las cartas figura de un jugador.",
             tags=["Juego"])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, db: Session = Depends(get_db)):
    return crud.partidas.get_cartas_figura_jugador(db=db, partida_id=partida_id, jugador_id=jugador_id)

@router.get('/{id_partida:int}/jugadores/{id_jugador:int}/cartas_movimiento',
            response_model=list[CartaMovimientoData],
            summary="Obtener cartas de movimiento de un jugador",
            description="Devuelve las cartas de movimiento de un jugador.",
            tags=["Juego"])
async def get_movimientos_jugador(id_partida: int, id_jugador: int, db: Session = Depends(get_db)):
    return crud.juego.get_movimientos_jugador(db, id_partida, id_jugador)

@router.get('/{id_partida:int}/turno',
            response_model=TurnoDetails,
            summary="Obtener la información de quien posee el turno.",
            description="Devuelve el nombre y el identificador de quien posee el turno en una partida.",
            tags=["Juego"])
async def get_turno_details(id_partida: int,  db: Session = Depends(get_db)):
    return crud.juego.get_turno_details(db=db, partida_id=id_partida)

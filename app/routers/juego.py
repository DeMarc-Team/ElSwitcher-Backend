from fastapi import (
    APIRouter, 
    Depends
)

from sqlalchemy.orm import Session

import crud.juego
import crud.partidas
from models import Base
from schemas import JuegoDetails, CartaFiguraData, CartaMovimientoData
from database import engine, get_db


Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/juego",
    tags=["juego"]
)

# TODO: Terminar de adaptar este endpoint a la especificación.
@router.get('/{partida_id: int}',
            response_model=JuegoDetails,
            summary="Obtener detalles de un turno",
            description="Devuelve los detalles de un turno.",
            tags=["Juego"])
async def get_turno_details(partida_id: int,  db: Session = Depends(get_db)):
    return crud.partidas.get_juego_details(db=db, partida_id=partida_id)

@router.get('/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura',
             response_model=list[CartaFiguraData],
             summary="Obtener cartas figura de un jugador",
             description="Devuelve las cartas figura de un jugador.",
             tags=["Juego"])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, db: Session = Depends(get_db)):
    return crud.partidas.get_cartas_figura_jugador(db=db, partida_id=partida_id, jugador_id=jugador_id)

@router.get('/{id_partida:int}/jugadores/{id_jugador:int}/cartas_movimiento', response_model=list[CartaMovimientoData])
async def get_movimientos_jugador(id_partida: int, id_jugador: int, db: Session = Depends(get_db)):
    return crud.juego.get_movimientos_jugador(db, id_partida, id_jugador)
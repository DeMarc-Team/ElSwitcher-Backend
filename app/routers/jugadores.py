from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status
)

from sqlalchemy.orm import Session
from http import HTTPStatus

import crud.jugadores as crud
import crud.exceptions as PartidaNotFoundError
from models.jugadores import Base, Jugador
from database import engine, get_db

from schemas.jugadores import JugadorData, JugadorOnCreateResponse

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.get('/{partida_id:int}/jugadores', response_model=list[JugadorOnCreateResponse])
async def get_jugadores(partida_id: int, db: Session = Depends(get_db)):
    jugadores = crud.get_jugadores(db, partida_id)
    return jugadores

@router.post('/{partida_id:int}/jugadores', response_model=JugadorOnCreateResponse)
async def join_to_partida(partida_id: int, jugador:JugadorData, db: Session = Depends(get_db)):
        try:
            jugador = crud.create_jugador(db, Jugador(nombre=jugador.nombre, partida_id=partida_id))
        except PartidaNotFoundError():
            pass ##
        # WARNING: If we leave it like this, then a disconnection could produce "dangling jugadors" (if we don't give a medium for reconnecting)
        return jugador
from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

import crud.jugadores as crud
from models import Base, Jugador
from database import engine, get_db
from schemas import JugadorData, JugadorOnCreateResponse
from websockets_manager.ws_home_manager import ws_home_manager
from websockets_manager.ws_partida_manager import ws_partida_manager

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
    await ws_home_manager.send_actualizar_partidas()
    await ws_partida_manager.send_actualizar_sala_espera(partida_id)
    return crud.create_jugador(db, Jugador(nombre=jugador.nombre, partida_id=partida_id))

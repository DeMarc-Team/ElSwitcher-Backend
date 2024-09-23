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

from crud.exceptions import PartidaNotFoundError, PartidaLlenaError
import crud.jugadores as crud
from models import Base, Jugador
from database import engine, get_db
from schemas import JugadorData, JugadorOnCreateResponse

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.get('/{partida_id:int}/jugadores', response_model=list[JugadorOnCreateResponse])
async def get_jugadores(partida_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_jugadores(db, partida_id)
    except PartidaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida Not Found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('/{partida_id:int}/jugadores', response_model=JugadorOnCreateResponse)
async def join_to_partida(partida_id: int, jugador:JugadorData, db: Session = Depends(get_db)):
    try:
        return crud.create_jugador(db, Jugador(nombre=jugador.nombre, partida_id=partida_id))
    except PartidaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida Not Found")
    except PartidaLlenaError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partida Full")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
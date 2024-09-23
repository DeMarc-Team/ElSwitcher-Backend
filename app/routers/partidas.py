from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends
)

from sqlalchemy.orm import Session
from fastapi import status

from crud.exceptions import PartidaNotFoundError, JuegoNotFoundError, PartidaYaIniciada
import crud.partidas as crud
from models import Base
from database import engine, get_db
from schemas import PartidaData, PartidaDetails, JuegoDetails

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.get('/', response_model=list[PartidaDetails]) #
async def get_partidas(db: Session = Depends(get_db)):
    try:
        return crud.get_partidas(db)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get('/{partida_id:int}', response_model=PartidaDetails)
async def get_partida_details(partida_id: int, db: Session = Depends(get_db)):
    try:
        return crud.get_partida_details(db, partida_id)
    except PartidaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida Not Found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('/', response_model=PartidaDetails)
async def create_partida(partida: PartidaData, db: Session = Depends(get_db)):
    try:
        return crud.create_partida(db=db, partida=partida)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.put('/{partida_id: int}')
async def iniciar_partida(partida_id: int, db: Session = Depends(get_db)):
    try:
        crud.iniciar_partida(db=db, id=partida_id)
    except PartidaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida Not Found")
    except PartidaYaIniciada as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partida ya Iniciada")
    
# TODO: Terminar la especificación de este endpoint para que retorne únicamente los valores que se desean para el turno
@router.get('/juego/{partida_id: int}', response_model=JuegoDetails)
async def get_turno_details(partida_id: int,  db: Session = Depends(get_db)):
    try:
        return crud.get_juego_details(db=db, partida_id=partida_id)
    except PartidaNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida Not Found")
    except JuegoNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Juego Not Found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
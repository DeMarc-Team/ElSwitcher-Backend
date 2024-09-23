from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends
)

from sqlalchemy.orm import Session
from fastapi import status

from crud.exceptions import PartidaNotFoundError
import crud.partidas as crud
from models import Base
from database import engine, get_db
from schemas import PartidaData, PartidaDetails

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
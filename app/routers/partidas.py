from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends
)

from sqlalchemy.orm import Session
from http import HTTPStatus

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
    return crud.get_partidas(db)

@router.post('/', response_model=PartidaDetails)
async def create_partida(partida: PartidaData, db: Session = Depends(get_db)):
    return crud.create_partida(db=db, partida=partida)
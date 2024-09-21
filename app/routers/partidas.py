from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends
)

from sqlalchemy.orm import Session
from http import HTTPStatus

import app.crud.partidas as crud
from app.models.partidas import Base
from app.database import engine, get_db
from app.schemas.partidas import PartidaData, PartidaId

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.get('/', response_model=list[PartidaId]) #
async def get_partidas(db: Session = Depends(get_db)):
    return crud.get_partidas(db)

@router.post('/', response_model=PartidaId)
async def create_partida(partida: PartidaData, db: Session = Depends(get_db)):
    return crud.create_partida(db=db, partida=partida)
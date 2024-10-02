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

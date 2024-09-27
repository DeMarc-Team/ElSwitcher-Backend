from fastapi import (
    APIRouter, 
    Depends
)

from sqlalchemy.orm import Session
from fastapi import status

import crud.partidas as crud
from models import Base
from database import engine, get_db
from schemas import PartidaData, PartidaDetails, PartidaDetails2, JuegoDetails, CartaFiguraData

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas",
    tags=["partidas"]
)

@router.get('/', response_model=list[PartidaDetails])
async def get_partidas(db: Session = Depends(get_db)):
    return crud.get_partidas(db)

@router.get('/{partida_id:int}', response_model=PartidaDetails2)
async def get_partida_details(partida_id: int, db: Session = Depends(get_db)):
        response = crud.get_partida_details(db, partida_id)
        espacios_disponibles = 4 - len(response.jugadores)
        id_creador = crud.get_id_creador(db, partida_id)
        partidaDetails = {
            "id": response.id,
            "nombre_partida": response.nombre_partida,
            "nombre_creador": response.nombre_creador,
            "id_creador": id_creador,
            "iniciada": response.iniciada,
            "espacios_disponibles": espacios_disponibles}
        return partidaDetails

@router.post('/', response_model=PartidaDetails)
async def create_partida(partida: PartidaData, db: Session = Depends(get_db)):
    return crud.create_partida(db=db, partida=partida)

@router.put('/{partida_id:int}', status_code=200)
async def iniciar_partida(partida_id: int, db: Session = Depends(get_db)):
    crud.iniciar_partida(db=db, id=partida_id)
    return {"message": "Partida iniciada correctamemte", "partida_id": partida_id}

# TODO: Terminar la especificación de este endpoint para que retorne únicamente los valores que se desean para el turno
@router.get('/juego/{partida_id: int}', response_model=JuegoDetails)
async def get_turno_details(partida_id: int,  db: Session = Depends(get_db)):
    return crud.get_juego_details(db=db, partida_id=partida_id)

@router.get('/juego/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura', response_model=list[CartaFiguraData])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, db: Session = Depends(get_db)):
    return crud.get_cartas_figura_jugador(db=db, partida_id=partida_id, jugador_id=jugador_id)

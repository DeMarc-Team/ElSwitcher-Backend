from fastapi import (
    APIRouter, 
    Depends
)

from sqlalchemy.orm import Session

import crud.partidas as crud
from database import get_db
from schemas import PartidaData, PartidaDetails, PartidaDetails2, JuegoDetails, CartaFiguraData

router = APIRouter(
    prefix="/partidas"
)

@router.get('/',
            response_model=list[PartidaDetails],
            summary="Obtener partidas",
            description="Devuelve la lista de partidas disponibles.",
            tags=["Partidas"])
async def get_partidas(db: Session = Depends(get_db)):
    return crud.get_partidas(db)

@router.get('/{partida_id:int}',
            response_model=PartidaDetails2,
            summary="Obtener detalles de una partida",
            description="Devuelve los detalles de la partida especificada por partida_id.",
            tags=["Partidas"])
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

@router.post('/',
             response_model=PartidaDetails,
             summary="Crear partida",
             description="Crea una nueva partida.",
             tags=["Partidas"])
async def create_partida(partida: PartidaData, db: Session = Depends(get_db)):
    return crud.create_partida(db=db, partida=partida)

@router.put('/{partida_id:int}',
            summary="Iniciar partida",
            description="Actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"])
async def iniciar_partida(partida_id: int, db: Session = Depends(get_db)):
    crud.iniciar_partida(db=db, id=partida_id)
    return {"message": "Partida iniciada correctamemte", "partida_id": partida_id}

@router.delete('/{partida_id:int}/jugadores/{jugador_id:int}',
            summary="Abandonar partida",
            description="Elimina al jugador, decide si termiar la partida y actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"],
            status_code=200)
async def abandonar_partida(partida_id: int, jugador_id : int, db: Session = Depends(get_db)):
    crud.abandonar_partida(db=db, partida_id=partida_id, jugador_id=jugador_id)
    return {"detail": "El jugador abandonó la partida exitosamente"}
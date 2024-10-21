from fastapi import (
    APIRouter, 
    Depends,
    WebSocket,
    WebSocketDisconnect
)

from sqlalchemy.orm import Session

import crud.partidas as crud
from models import Base
from database import engine, get_db
from schemas import PartidaData, GetPartida, PartidaDetails, PartidaDetails2, JuegoDetails, CartaFiguraData
from websockets_manager.ws_home_manager import ws_home_manager
from websockets_manager.ws_partidas_manager import ws_partidas_manager

Base.metadata.create_all(bind=engine)

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas"
)

@router.get('/',
            response_model=list[GetPartida],
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
    partida_details = crud.create_partida(db=db, partida=partida)
    await ws_home_manager.send_actualizar_partidas()
    return partida_details

@router.put('/{partida_id:int}',
            summary="Iniciar partida",
            description="Actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"])
async def iniciar_partida(partida_id: int, db: Session = Depends(get_db)):
    crud.iniciar_partida(db=db, id=partida_id)
    await ws_home_manager.send_actualizar_partidas()
    await ws_partidas_manager.send_actualizar_sala_espera(partida_id)
    return {"details": "Partida iniciada correctamemte", "partida_id": partida_id}

@router.delete('/{partida_id:int}/jugadores/{jugador_id:int}',
            summary="Abandonar partida",
            description="Elimina al jugador, decide si termiar la partida y actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"],
            status_code=200)
async def abandonar_partida(partida_id: int, jugador_id : int, db: Session = Depends(get_db)):
    eventos = crud.abandonar_partida(db=db, partida_id=partida_id, jugador_id=jugador_id)

    hay_ganador = eventos.get("hay_ganador")
    partida_cancelada = eventos.get("partida_cancelada")
    if (hay_ganador):
        ganador_id = hay_ganador.get("id_ganador")
        ganador_nombre = hay_ganador.get("nombre_ganador")
        await ws_partidas_manager.send_hay_ganador(partida_id, ganador_id, ganador_nombre)
    elif (partida_cancelada):
        partida_id = partida_cancelada.get("id")
        await ws_partidas_manager.send_partida_cancelada(partida_id)
        await ws_home_manager.send_actualizar_partidas()
    else:
        await ws_home_manager.send_actualizar_partidas()
        await ws_partidas_manager.send_actualizar_turno(partida_id)
        await ws_partidas_manager.send_actualizar_sala_espera(partida_id)
        await ws_partidas_manager.send_actualizar_tablero(partida_id) # Se deshacen movimientos parciales si abandona
    return {"detail": "El jugador abandonó la partida exitosamente"}

@router.websocket('/')
async def start_home_socket(websocket: WebSocket):
    try:
        user_id = await ws_home_manager.connect(websocket)
        
        while True:
            data = await websocket.receive_json()
            print(f"Websocket received: {data}")
        
    except WebSocketDisconnect:
        ws_home_manager.disconnect(user_id)
        
@router.websocket('/{partida_id:int}/jugador/{jugador_id:int}')
async def start_partida_socket(partida_id: int, jugador_id: int, websocket: WebSocket):
    try:
        await ws_partidas_manager.connect(partida_id, jugador_id, websocket)
        
        while True:
            data = await websocket.receive_json()
            print(f"Websocket received: {data}")
        
    except WebSocketDisconnect:
        ws_partidas_manager.disconnect(partida_id, jugador_id)
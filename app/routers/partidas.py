from fastapi import (
    APIRouter, 
    Depends,
    WebSocket,
    WebSocketDisconnect
)
from sqlalchemy.orm import Session
from db.models import Base
from db.database import engine, get_db
from controllers.PartidaController import PartidaController
from schemas import PartidaData, GetPartida, PartidaDetails, PartidaDetails2, JugadorOnCreateResponse, JugadorData, FromUnirsePartida

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/partidas"
)

# Dependencia para el controlador de partida
async def get_partida_controller(db: Session = Depends(get_db)):
    return PartidaController(db)

@router.get('/',
            response_model=list[GetPartida],
            summary="Obtener partidas",
            description="Devuelve la lista de partidas disponibles.",
            tags=["Partidas"])
async def get_partidas(controller: PartidaController = Depends(get_partida_controller)):
    return await controller.get_partidas()

@router.get('/{partida_id:int}',
            response_model=PartidaDetails2,
            summary="Obtener detalles de una partida",
            description="Devuelve los detalles de la partida especificada por partida_id.",
            tags=["Partidas"])
async def get_partida_details(partida_id: int, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.get_partida_details(partida_id)

@router.post('/',
             response_model=PartidaDetails,
             summary="Crear partida",
             description="Crea una nueva partida.",
             tags=["Partidas"])
async def create_partida(partida: PartidaData, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.create_partida(partida)

@router.put('/{partida_id:int}',
            summary="Iniciar partida",
            description="Actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"])
async def iniciar_partida(partida_id: int, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.iniciar_partida(partida_id)

@router.delete('/{partida_id:int}/jugadores/{jugador_id:int}',
            summary="Abandonar partida",
            description="Elimina al jugador, decide si terminar la partida y actualiza los datos de la partida especificada por partida_id.",
            tags=["Partidas"],
            status_code=200)
async def abandonar_partida(partida_id: int, jugador_id: int, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.abandonar_partida(partida_id, jugador_id)

@router.get('/{partida_id:int}/jugadores',
            response_model=list[JugadorOnCreateResponse],
            summary="Obtener jugadores de una partida",
            description="Devuelve la lista de jugadores que pertenecen a la partida especificada por partida_id.",
            tags=["Jugadores"])
async def get_jugadores(partida_id: int, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.get_jugadores(partida_id)

@router.post('/{partida_id:int}/jugadores',
             response_model=JugadorOnCreateResponse,
             summary="Unirse a una partida",
             description="Crea un nuevo jugador, para el usuario, en la partida especificada por partida_id.",
             tags=["Jugadores"])
async def join_to_partida(partida_id: int, datos_para_unirse: FromUnirsePartida, controller: PartidaController = Depends(get_partida_controller)):
    return await controller.join_to_partida(partida_id, datos_para_unirse.nombre, datos_para_unirse.contraseña)


# FIXME: Esto si quizas deberia ir en otro archivo
from websockets_manager.ws_home_manager import ws_home_manager
from websockets_manager.ws_partidas_manager import ws_partidas_manager

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
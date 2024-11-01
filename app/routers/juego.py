from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base
from controllers.JuegoController import JuegoController
from schemas import CartaFiguraData, CartaMovimientoData, TurnoDetails, TableroData, CasillasMov, MovimientoParcialData, CompletarFiguraData

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/juego")

# Crear una dependencia para el controlador
async def get_game_controller(db: Session = Depends(get_db)):
    return JuegoController(db)

@router.get('/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura',
            response_model=list[CartaFiguraData],
            summary="Obtener cartas figura de un jugador",
            description="Devuelve las cartas figura de un jugador.",
            tags=["Juego"])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_cartas_figura_jugador(partida_id, jugador_id)

@router.get('/{id_partida:int}/jugadores/{jugador_id:int}/cartas_movimiento',
            response_model=list[CartaMovimientoData],
            summary="Obtener cartas de movimiento de un jugador",
            description="Devuelve las cartas de movimiento de un jugador.",
            tags=["Juego"])
async def get_movimientos_jugador(id_partida: int, jugador_id: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_movimientos_jugador(id_partida, jugador_id)

@router.get('/{id_partida:int}/turno',
            response_model=TurnoDetails,
            summary="Obtener la información de quien posee el turno.",
            description="Devuelve el nombre y el identificador de quien posee el turno en una partida.",
            tags=["Juego"])
async def get_turno_details(id_partida: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_turno_details(id_partida)

@router.put('/{id_partida:int}/jugadores/{jugador_id:int}/turno',
            summary="Terminar el turno del jugador actual.",
            description="Termina el turno del jugador actual, si es que el id del mismo coincide con el del parámetro.",
            tags=["Juego"])
async def terminar_turno(id_partida: int, jugador_id: int, controller: JuegoController = Depends(get_game_controller)):
    await controller.terminar_turno(id_partida, jugador_id)

@router.get('/{id_partida:int}/tablero',
            summary='Obetener el tablero del juego',
            response_model=TableroData,
            tags=["Juego"])
async def get_tablero(id_partida: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_tablero(id_partida)

@router.put('/{id_partida}/jugadores/{jugador_id}/tablero/casilla',
            summary="Jugar carta movimiento.",
            description="Modificar el tablero según las coordenadas de las fichas que envía el jugador del turno actual.",
            tags=["Juego"])
async def modificar_casillas(id_partida: int, jugador_id: int, coordenadas: CasillasMov, controller: JuegoController = Depends(get_game_controller)):
    await controller.modificar_casillas(id_partida, jugador_id, coordenadas)

@router.delete('/{id_partida}/jugadores/{jugador_id}/mov-parciales',
               summary="Eliminar el último movimiento parcial de un jugador.",
               tags=["Juego"])
async def deshacer_movimiento(id_partida: int, jugador_id: int, controller: JuegoController = Depends(get_game_controller)):
    await controller.deshacer_movimiento(id_partida)

@router.get('/{id_partida}/jugadores/{jugador_id}/mov-parciales',
               summary="Obtiene el stack de los movimientos parciales",
               response_model=list[MovimientoParcialData],
               tags=["Juego"])
async def get_movimientos_parciales(id_partida: int, jugador_id: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_movimientos_parciales(id_partida)

@router.put('/{id_partida:int}/jugadores/{jugador_id:int}/tablero/figura',
            summary="Completar figura propia",
            description="Utiliza la carta de figura especificada a partir de la existencia de la figura en las coordenadas que se pasaron.",
            tags=["Juego"])
async def completar_figura_propia(id_partida: int, jugador_id: int, figura_data: CompletarFiguraData, controller: JuegoController = Depends(get_game_controller)):
    await controller.completar_figura_propia(id_partida, jugador_id, figura_data)

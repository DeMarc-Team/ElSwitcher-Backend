from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base
from controllers.JuegoController import JuegoController
from schemas import (
    CartaFiguraData,
    CartaMovimientoData,
    TurnoDetails,
    TableroData,
    CasillasMov,
    MovimientoParcialData,
    CompletarFiguraData,
    BloquearFiguraData
)

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

@router.get('/{id_partida:int}/jugadores/{id_jugador:int}/cartas_movimiento',
            response_model=list[CartaMovimientoData],
            summary="Obtener cartas de movimiento de un jugador",
            description="Devuelve las cartas de movimiento de un jugador.",
            tags=["Juego"])
async def get_movimientos_jugador(id_partida: int, id_jugador: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_movimientos_jugador(id_partida, id_jugador)

@router.get('/{id_partida:int}/turno',
            response_model=TurnoDetails,
            summary="Obtener la información de quien posee el turno.",
            description="Devuelve el nombre y el identificador de quien posee el turno en una partida.",
            tags=["Juego"])
async def get_turno_details(id_partida: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_turno_details(id_partida)

@router.put('/{id_partida:int}/jugadores/{id_jugador:int}/turno',
            summary="Terminar el turno del jugador actual.",
            description="Termina el turno del jugador actual, si es que el id del mismo coincide con el del parámetro.",
            tags=["Juego"])
async def terminar_turno(id_partida: int, id_jugador: int, controller: JuegoController = Depends(get_game_controller)):
    await controller.terminar_turno(id_partida, id_jugador)

@router.get('/{id_partida:int}/tablero',
            summary='Obetener el tablero del juego',
            response_model=TableroData,
            tags=["Juego"])
async def get_tablero(id_partida: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_tablero(id_partida)

@router.put('/{id_partida}/jugadores/{id_jugador}/tablero/casilla',
            summary="Jugar carta movimiento.",
            description="Modificar el tablero según las coordenadas de las fichas que envía el jugador del turno actual.",
            tags=["Juego"])
async def modificar_casillas(id_partida: int, id_jugador: int, coordenadas: CasillasMov, controller: JuegoController = Depends(get_game_controller)):
    await controller.modificar_casillas(id_partida, id_jugador, coordenadas)

@router.delete('/{id_partida}/jugadores/{id_jugador}/mov-parciales',
               summary="Eliminar el último movimiento parcial de un jugador.",
               tags=["Juego"])
async def deshacer_movimiento(id_partida: int, id_jugador: int, controller: JuegoController = Depends(get_game_controller)):
    await controller.deshacer_movimiento(id_partida)

@router.get('/{id_partida}/jugadores/{id_jugador}/mov-parciales',
               summary="Obtiene el stack de los movimientos parciales",
               response_model=list[MovimientoParcialData],
               tags=["Juego"])
async def get_movimientos_parciales(id_partida: int, id_jugador: int, controller: JuegoController = Depends(get_game_controller)):
    return await controller.get_movimientos_parciales(id_partida)

@router.put('/{id_partida:int}/jugadores/{id_jugador:int}/tablero/figura',
            summary="Completar figura propia",
            description="Utiliza la carta de figura especificada a partir de la existencia de la figura en las coordenadas que se pasaron.",
            tags=["Juego"])
async def completar_figura_propia(id_partida: int, id_jugador: int, figura_data: CompletarFiguraData, controller: JuegoController = Depends(get_game_controller)):
    await controller.completar_figura_propia(id_partida, id_jugador, figura_data)

@router.put('/{id_partida}/jugadores/{id_jugador}/bloquear-carta',
            summary="Bloquear una figura ajena",
            description="Utiliza la carta de figura especificada para bloquear el jugador del id que se pasó. La figura y su color deben estar disponibles y el otro jugador debe tener su respectiva carta.",
            tags=["Juego"])
async def bloquear_carta_ajena(id_partida: int, id_jugador: int, bloqueo_data: BloquearFiguraData, controller: JuegoController = Depends(get_game_controller)):
    await controller.bloquear_carta_ajena(id_partida, id_jugador, bloqueo_data)


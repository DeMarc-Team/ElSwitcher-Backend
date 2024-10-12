from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

import crud.juego
import crud.partidas
from models import Base
from schemas import CartaFiguraData, CartaMovimientoData, TurnoDetails, TableroData, CasillasMov
from database import engine, get_db

from websockets_manager.ws_partidas_manager import ws_partidas_manager

Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/juego"
)


@router.get('/{partida_id:int}/jugadores/{jugador_id:int}/cartas_figura',
            response_model=list[CartaFiguraData],
            summary="Obtener cartas figura de un jugador",
            description="Devuelve las cartas figura de un jugador.",
            tags=["Juego"])
async def get_cartas_figura_jugador(partida_id: int, jugador_id: int, db: Session = Depends(get_db)):
    return crud.partidas.get_cartas_figura_jugador(db=db, partida_id=partida_id, jugador_id=jugador_id)


@router.get('/{id_partida:int}/jugadores/{id_jugador:int}/cartas_movimiento',
            response_model=list[CartaMovimientoData],
            summary="Obtener cartas de movimiento de un jugador",
            description="Devuelve las cartas de movimiento de un jugador.",
            tags=["Juego"])
async def get_movimientos_jugador(id_partida: int, id_jugador: int, db: Session = Depends(get_db)):
    return crud.juego.get_movimientos_jugador(db, id_partida, id_jugador)


@router.get('/{id_partida:int}/turno',
            response_model=TurnoDetails,
            summary="Obtener la información de quien posee el turno.",
            description="Devuelve el nombre y el identificador de quien posee el turno en una partida.",
            tags=["Juego"])
async def get_turno_details(id_partida: int,  db: Session = Depends(get_db)):
    return crud.juego.get_turno_details(db=db, partida_id=id_partida)


@router.put('/{id_partida:int}/jugadores/{id_jugador:int}/turno',
            summary="Terminar el turno del jugador actual.",
            description="Termina el turno del jugador actual, si es que el id del mismo coincide con el del parámetro.",
            tags=["Juego"])
async def terminar_turno(id_partida: int, id_jugador, db: Session = Depends(get_db)):
    crud.juego.terminar_turno(db, id_partida, id_jugador)
    await ws_partidas_manager.send_actualizar_turno(id_partida)


@router.get('/{id_partida:int}/tablero',
            summary='Obetener el tablero del juego',
            response_model=TableroData,
            tags=["Juego"])
async def get_tablero(id_partida: int, db: Session = Depends(get_db)):
    """Obtiene el tablero de una partida

    Args:
        id_partida (int): id de la partida

    Returns:
        Tablero de la partida en formato JSON

    Details:
        Response 200 en caso de que el tablero se haya obtenido correctamente.
        Response 404 en caso de que la partida no exista o no haya sido iniciada.
    """
    from figuras import hallar_todas_las_figuras_en_tablero  
    import json  
    tablero = crud.juego.get_tablero(db, id_partida)
    tablero_desearilizado = json.loads(tablero)
    response = {
        'tablero': tablero_desearilizado,
        'figuras_a_resaltar': hallar_todas_las_figuras_en_tablero(tablero_desearilizado)
    }
    return response



@router.put('/{id_partida}/jugadores/{id_jugador}/tablero/casilla',
            summary="Jugar carta movimiento.",
            description="Modificar el tablero segun las coordenadas de las fichas que envia el jugador del tueno actual.",
            tags=["Juego"])
async def modificar_casillas(id_partida: int, id_jugador: int, coordenadas: CasillasMov, db: Session = Depends(get_db)):
    crud.juego.modificar_casillas(
        id_partida, id_jugador, coordenadas, db)
    await ws_partidas_manager.send_actualizar_tablero(id_partida)
    # await ws_partidas_manager.send_actualizar_cartas_movimiento(id_partida) # Comentado porque el front no implementa el handle para esto

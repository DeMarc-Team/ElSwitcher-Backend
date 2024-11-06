from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated

class PartidaData(BaseModel):
    nombre_partida: str
    nombre_creador: str

class PartidaDetails(PartidaData):
    id: int
    nombre_partida: str
    nombre_creador: str
    id_creador: int
    iniciada: bool

class GetPartida(PartidaData): #Listar partidas
    id: int
    nombre_partida: str
    nombre_creador: str
    id_creador: int
    iniciada: bool
    numero_de_jugadores: int

class PartidaDetails2(PartidaData):
    id: int
    nombre_partida: str
    nombre_creador: str
    id_creador: int | None
    iniciada: bool
    espacios_disponibles: int
    #jugadores: list[jugador] = []

class JugadorData(BaseModel):
    nombre: str

class JugadorOnCreateResponse(JugadorData):
    id_jugador: int

CoordenadasFiguraResaltada = list[tuple[int,int]]

class TableroData(BaseModel):
    tablero: list[list[int]]
    figuras_a_resaltar: dict[str,list[CoordenadasFiguraResaltada]]
    
class JuegoData(BaseModel):
    pass

class JuegoDetails(JuegoData):
    id: int
    id_jugador: int
    partida_id: int

class TurnoDetails(BaseModel):
    id_jugador: int
    nombre_jugador: str

class CartaFiguraData(BaseModel):
    figura: str
    bloqueada: bool

class CartaMovimientoData(BaseModel):
    movimiento: str
    usada_en_movimiento_parcial: bool

class Casilla(BaseModel):
    row: int
    col: int

class CasillasMov(BaseModel):
    casilla1: Casilla
    casilla2: Casilla
    codeMove: str

class MovimientoParcialData(BaseModel):
    origen: str
    destino: str
    orden: int
    movimiento: str    

class CompletarFiguraData(BaseModel):
    figura: list[Casilla]
    carta_fig: str
    
class BloquearFiguraData(BaseModel):
    id_jugador_bloqueado: int
    figura: list[Casilla]
    carta_fig: str

class ResponseCronometro(BaseModel):
    inicio: str
    duracion: int
class RespuestaColorProhibido(BaseModel):
    color: Annotated[int, Field(ge=1, le=4)] | None
    
    @field_validator("color", mode="before")
    def validate_color(cls, value):
        if isinstance(value,int) and (1 <= value <= 4):
            return value
        return None

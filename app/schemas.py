from pydantic import BaseModel

class PartidaData(BaseModel):
    nombre_partida: str
    nombre_creador: str

class PartidaDetails(PartidaData):
    id: int
    nombre_partida: str
    nombre_creador: str
    id_creador: int
    iniciada: bool

class PartidaDetails2(PartidaData):
    id: int
    nombre_partida: str
    nombre_creador: str
    id_creador: int
    iniciada: bool
    espacios_disponibles: int
    #jugadores: list[jugador] = []

class JugadorData(BaseModel):
    nombre: str

class JugadorOnCreateResponse(JugadorData):
    id_jugador: int

    

class JuegoData(BaseModel):
    pass

class JuegoDetails(JuegoData):
    id: int
    turno: int
    partida_id: int



class CartaFiguraData(BaseModel):
    figura: str
    revelada: bool



class CartaMovimientoData(BaseModel):
    movimiento: str
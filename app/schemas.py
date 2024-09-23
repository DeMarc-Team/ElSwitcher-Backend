from pydantic import BaseModel

class PartidaData(BaseModel):
    nombre_partida: str
    nombre_creador: str

class PartidaDetails(PartidaData):
    id: int
    iniciada: bool
    # creador_id: int
    nombre_creador: str
    # espacios_disponibles: int
    # #jugadores: list[jugador] = []



class JugadorData(BaseModel):
    nombre: str

class JugadorOnCreateResponse(JugadorData):
    id_jugador: int
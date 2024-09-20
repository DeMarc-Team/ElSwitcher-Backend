from pydantic import BaseModel

class PartidaData(BaseModel):
    nombre_partida: str
    nombre_creador: str

class PartidaId(PartidaData):
    id: int
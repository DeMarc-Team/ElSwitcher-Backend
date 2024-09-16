from pydantic import BaseModel

class PartidaData(BaseModel):
    nombre: str
    iniciada: bool

class PartidaId(PartidaData):
    id: int
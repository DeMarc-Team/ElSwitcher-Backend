from pydantic import BaseModel

class JugadorData(BaseModel):
    nombre: str

class JugadorOnCreateResponse(JugadorData):
    id_jugador: int
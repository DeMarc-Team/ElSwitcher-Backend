from sqlalchemy.orm import Session

from exceptions import ResourceNotFoundError, ForbiddenError
from models import Partida, Jugador
from schemas import TurnoDetails

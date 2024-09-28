from fastapi import FastAPI

from routers import partidas, jugadores, juego
from fastapi.middleware.cors import CORSMiddleware
from exceptions import ResourceNotFoundError, ForbiddenError, resource_not_found_handler, forbidden_error_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(partidas.router)
app.include_router(jugadores.router)
app.include_router(juego.router)

# Excepciones
app.add_exception_handler(ResourceNotFoundError, resource_not_found_handler)
app.add_exception_handler(ForbiddenError, forbidden_error_handler)


@app.get('/')
def root():
    return 'Test String'

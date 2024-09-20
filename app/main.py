from fastapi import FastAPI

from database import engine
from routers import partidas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(partidas.router)


@app.get('/')
def root():
    return 'Test String'

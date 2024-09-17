from fastapi import FastAPI

from database import engine
from routers import partidas

app = FastAPI()


app.include_router(partidas.router)

@app.get('/')
def root():
    return 'Test String'

from fastapi import Request
from fastapi.responses import JSONResponse
# from fastapi.exceptions import HTTPException
from fastapi import status

#from main import app
from fastapi import FastAPI
app = FastAPI()

class ResourceNotFoundError(Exception):
    """Excepción lanzada cuando un recurso no se encuentra."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    # Registrar detalles de la solicitud que falló
    print(f"Request URL: {request.url}")
    print(f"Request Method: {request.method}")
    # Devolver una respuesta JSON con un código de estado 404
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )

class ForbiddenError(Exception):
    """Excepción lanzada cuando el acceso a un recurso está prohibido."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)
        
@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    # Registrar detalles de la solicitud que falló
    print(f"Request URL: {request.url}")
    print(f"Request Method: {request.method}")
    # Devolver una respuesta JSON con un código de estado 403
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message}
    )

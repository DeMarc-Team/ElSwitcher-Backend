from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi import status

class ResourceNotFoundError(Exception):
    """Excepción lanzada cuando un recurso no se encuentra."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    print("Resource not found error:", exc.message)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message}
    )

class ForbiddenError(Exception):
    """Excepción lanzada cuando el acceso a un recurso está prohibido."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)
        
async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    print("Forbidden error:", exc.message)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message}
    )

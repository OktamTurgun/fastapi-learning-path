from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic validatsiya xatolarini izchil formatga keltirish"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validatsiya xatosi", "errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Kutilmagan (dasturchi bashorat qilmagan) xatolarni ushlab qolish"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Serverda kutilmagan xatolik yuz berdi"},
    )
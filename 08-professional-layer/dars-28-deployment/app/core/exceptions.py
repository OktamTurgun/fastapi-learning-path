from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation xatoliklarini standart va chiroyli shaklda qaytarish"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Kiritilgan ma'lumotlar noto'g'ri",
            "errors": exc.errors()
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Barcha kutilmagan server xatoliklarini (500) tutish"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Serverda kutilmagan xatolik yuz berdi"}
    )

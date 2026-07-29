from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.routers import product, category, user

app = FastAPI(title="Storely API", version="1.0.0")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Storely API ishlamoqda"}


# Ishga tushirish: python -m uvicorn app.main:app --reload
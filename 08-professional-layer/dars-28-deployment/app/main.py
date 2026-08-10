from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import validation_exception_handler, generic_exception_handler
from app.routers import product, category, user, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Productionda Swagger'ni yopish imkoniyati
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Production CORS Sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlerlar
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(health.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "environment": settings.ENVIRONMENT,
        "health_check": "/health",
        "docs": "/docs" if settings.DEBUG else "Disabled in production"
    }

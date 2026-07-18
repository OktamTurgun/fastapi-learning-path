from fastapi import FastAPI

from app.routers import customer, order

app = FastAPI(title="Storely Orders CRUD", version="1.0.0")

app.include_router(customer.router)
app.include_router(order.router)


@app.get("/")
def root():
    return {"message": "Storely Orders CRUD demo ishlamoqda"}
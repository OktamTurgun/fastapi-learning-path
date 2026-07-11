"""
Dars 10 — Mustaqil mashq: Storely — Xodim (Employee) tizimi

Vazifa:

1. `EmployeeCreate` modelini yarating (request uchun):
   - full_name: str, min_length=2
   - email: EmailStr
   - salary: float, gt=0
   - pin_code: str, min_length=4   (bu maydon response'da KO'RINMASLIGI kerak!)

2. `EmployeeResponse` modelini yarating (response uchun):
   - id: int
   - full_name: str
   - email: EmailStr
   - salary: float
   (pin_code YO'Q!)

3. `InventoryItemResponse` modelini yarating — alias bilan:
   - id: int
   - item_name: str = Field(..., alias="itemName")
   - unit_cost: float = Field(..., alias="unitCost")
   - stock_count: int = Field(..., alias="stockCount")
   - model_config orqali populate_by_name=True qiling

   Bonus: @computed_field bilan `total_cost` qo'shing
   (unit_cost * stock_count).

4. In-memory employees_db, next_employee_id yarating.

5. POST "/employees" — EmployeeCreate qabul qilib, response_model=
   EmployeeResponse bilan javob bersin, status_code=201.
   (pin_code javobda YO'QLIGINI tekshiring!)

6. GET "/employees/{employee_id}" — response_model=EmployeeResponse
   bilan, 404 xato bilan.

7. Statik inventory_items ro'yxati yarating (kamida 2 ta element) va
   GET "/inventory/{item_id}" — response_model=InventoryItemResponse
   bilan qaytaring.

Test JSON (POST /employees uchun):
{
  "full_name": "Aziza Karimova",
  "email": "aziza@storely.uz",
  "salary": 4500000,
  "pin_code": "1234"
}

Tekshirish: javobda "pin_code" maydoni HECH QACHON ko'rinmasligi kerak.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field

app = FastAPI(title="Storely Employee API", version="1.0.0")


# TODO: EmployeeCreate modelini yarating
class EmployeeCreate(BaseModel):
  full_name: str = Field(..., min_length=2)
  email: EmailStr
  salary: float = Field(..., gt=0)
  pin_code: str = Field(..., min_length=4)


# TODO: EmployeeResponse modelini yarating (pin_code YO'Q)
class EmployeeResponse(BaseModel):
  id: int
  full_name: str
  email: EmailStr
  salary: float

# TODO: InventoryItemResponse modelini yarating (alias + computed_field bilan)
class InventoryItemResponse(BaseModel):
  model_config = ConfigDict(populate_by_name=True)
  id: int
  item_name: str = Field(..., alias="itemName")
  unit_cost: float = Field(..., alias="unitCost")
  stock_count: int = Field(..., alias="stockCount")

  @computed_field
  @property
  def total_value(self) -> float:
      return round(self.unit_cost * self.stock_count, 2)

# TODO: employees_db va next_employee_id yarating
employees_db: list[dict] = []
next_employee_id = 1


# TODO: inventory_items statik ro'yxatini yarating
inventory_items = [
    {"id": 1, "item_name": "Laptop", "unit_cost": 1500.0, "stock_count": 10},
    {"id": 2, "item_name": "Mouse", "unit_cost": 25.0, "stock_count": 50}
]


# TODO: POST "/employees" endpointini yozing (response_model bilan)
@app.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, tags=["Employees"])
def create_employee(employee: EmployeeCreate):
    global next_employee_id
    new_employee = {
        "id": next_employee_id,
        "full_name": employee.full_name,
        "email": employee.email,
        "salary": employee.salary,
        "pin_code": f"hashed_{employee.pin_code}"
    }
    employees_db.append(new_employee)
    next_employee_id += 1
    return new_employee





# TODO: GET "/employees/{employee_id}" endpointini yozing (404 bilan)
@app.get("/employees/{employee_id}", response_model=EmployeeResponse, tags=["Employees"])
def get_employee(employee_id: int):
    for employee in employees_db:
        if employee["id"] == employee_id:
            return employee
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")


# TODO: GET "/inventory/{item_id}" endpointini yozing (response_model bilan)
@app.get("/inventory/{item_id}", response_model=InventoryItemResponse, tags=["Inventory"])
def get_inventory_item(item_id: int):
    for item in inventory_items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
"""
Dars 04 — Mustaqil mashq: Orders router

Vazifa:
1. `router = APIRouter()` yarating (prefix bermang — buni main.py
   include_router() darajasida beramiz).

2. Quyidagi statik ma'lumotni yarating:
   fake_orders = [
       {"id": 1, "mijoz": "Botir", "summa": 150000},
       {"id": 2, "mijoz": "Dilnoza", "summa": 89000},
       {"id": 3, "mijoz": "Sardor", "summa": 230000},
   ]

3. "/" manzilida GET endpoint yarating — barcha orderlarni qaytarsin.

4. "/{order_id}" manzilida GET endpoint yarating — id bo'yicha bitta
   orderni topib qaytarsin (topilmasa {"xato": "Order topilmadi"}).

5. Bonus: "/summary" manzilida GET endpoint yarating — barcha
   orderlarning summasini qo'shib, {"jami_summa": ...} qaytaring.
   DIQQAT: bu endpointni "/{order_id}"dan OLDIN joylashtiring —
   aks holda FastAPI "/summary"ni ham order_id sifatida tushunishga
   harakat qiladi va xato beradi! (Bu muhim FastAPI xususiyati —
   routing yuqoridan pastga qarab, birinchi mos kelgan yo'lni tanlaydi)
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: fake_orders ro'yxatini yarating
fake_orders = [
       {"id": 1, "mijoz": "Botir", "summa": 150000},
       {"id": 2, "mijoz": "Dilnoza", "summa": 89000},
       {"id": 3, "mijoz": "Sardor", "summa": 230000},
   ] 


# TODO: "/summary" endpointini yozing (DIQQAT: "/{order_id}"dan OLDIN!)
@router.get("/summary")
def sum_orders():
  """Barcha buyurtmalar summasini qaytaradi"""
  jami_summa = sum(order["summa"] for order in fake_orders)
  return {"jami_summa": jami_summa}


# TODO: "/" endpointini yozing
@router.get("/")
def list_orders():
  """Barcha buyurtmalar ro'yxati"""
  return {"orders": fake_orders}
  



# TODO: "/{order_id}" endpointini yozing
@router.get("/{order_id}")
def get_order(order_id: int):
  """Bitta buyurtmani id orqali topish"""
  for order in fake_orders:
    if order["id"] == order_id:
      return order
  return {"Xato!": "Buyurtma topilmadi!"}
"""
Dars 05 — Mustaqil mashq: Task Manager API

Vazifa — "vazifalar" (tasks) uchun to'liq CRUD yarating:

1. In-memory ro'yxat yarating:
   tasks = [
       {"id": 1, "sarlavha": "FastAPI o'rganish", "bajarildi": False},
       {"id": 2, "sarlavha": "Git push qilish", "bajarildi": True},
   ]

2. GET "/tasks" — barcha vazifalarni qaytarsin.

3. GET "/tasks/{task_id}" — bitta vazifani qaytarsin.
   Topilmasa HTTPException bilan 404 qaytaring (detail: "Vazifa topilmadi").

4. POST "/tasks" — yangi vazifa qo'shsin (sarlavha: str, bajarildi: bool = False).
   status_code=201 bo'lishi kerak. Yangi id avtomatik hisoblansin.

5. PUT "/tasks/{task_id}" — vazifani TO'LIQ yangilasin
   (sarlavha VA bajarildi ikkalasi ham majburiy parametr bo'lsin).

6. PATCH "/tasks/{task_id}" — faqat "bajarildi" maydonini yangilasin.

7. DELETE "/tasks/{task_id}" — vazifani o'chirsin, status_code=204 qaytarsin.

Barcha "topilmadi" holatlarida HTTPException status_code=404 bilan
ishlatilishi SHART — oddiy {"xato": "..."} qaytarish YETARLI EMAS.
"""

from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Task Manager API", version="1.0.0")

# TODO: tasks ro'yxatini yarating
tasks = [
  {"id": 1, "sarlavha":"FastAPI o'rganish", "bajarildi": False},
  {"id": 2, "sarlavha":"Git pus qilish", "bajarildi": True},
]


# TODO: GET "/tasks" — barcha vazifalar
@app.get("/tasks", tags=["Tasks"])
def list_tasks():
  """Barcha vazifalar royxatini qaytaradi"""
  return {"tasks": tasks}


# TODO: GET "/tasks/{task_id}" — bitta vazifa (404 bilan)
@app.get("/tasks{task_id}", tags=["Tasks"])
def get_book(task_id: int):
  """Bitta vazifani id orqli olish. Agar task bo'lmasa 404 qaytaradi"""
  for task in tasks:
    if task["id"] == task_id:
      return task
  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Afsuski vazifa (id = {task_id}) topilmadi!",
  )


# TODO: POST "/tasks" — yangi vazifa (status_code=201)
@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(title: str, available: bool = True):
  """Yangi vazifa yaratish. Muvaffaqiyatli bo'lsa 201 qaytaradi"""
  new_id = max((t["id"] for t in tasks), default=0) + 1
  new_task = {"id": new_id, "title": title, "available": available}
  tasks.append(new_task)
  return new_task


# TODO: PUT "/tasks/{task_id}" — to'liq yangilash
@app.put("/tasks/{task_id}", tags=["Tasks"])
def replace_task(task_id: int, title: str, available: bool):
  """
    Vazifani TO'LIQ almashtiradi — shuning uchun PUT'da
    barcha maydonlar (title VA available) majburiy.
  """
  for task in tasks:
    if task["id"] == task_id:
      task["title"] = title 
      task["available"] = available
      return task
  raise HTTPException(status_code=404, detail="Afsuski vazifa topilmadi!")  


# TODO: PATCH "/tasks/{task_id}" — qisman yangilash (faqat bajarildi)
@app.patch("/tasks/{task_is}", tags=["Tasks"])
def update_task(task_id: int, available: bool):
  """
    Vazifani QISMAN yangilaydi — faqat 'available' maydonini
    o'zgartiradi, 'title' o'zgarishsiz qoladi.
  """
  for task in tasks:
    if task["id"] == task_id:
      task["available"] = available
      return task
  raise HTTPException(status_code=404, detail="Afsuski vazifa topilmadi!")


# TODO: DELETE "/tasks/{task_id}" — o'chirish (status_code=204)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int):
  """Vazifani ro'yxatdan o'chiradi. Muvaffaqiyatli bo'lsa, body qaytmaydi (402)."""
  for i, task in enumerate(tasks):
    if task["id"] == task_id:
      tasks.pop(i)
      return None
  raise HTTPException(status_code=404, detail="Afsuski vazifa topilmadi!")  
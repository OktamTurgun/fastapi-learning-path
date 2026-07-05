from fastapi import FastAPI, HTTPException, status

app = FastAPI(title="Task Manager API", version="1.0.0")

tasks = [
    {"id": 1, "sarlavha": "FastAPI o'rganish", "bajarildi": False},
    {"id": 2, "sarlavha": "Git push qilish", "bajarildi": True},
]


@app.get("/tasks", tags=["Tasks"])
def list_tasks():
    """Barcha vazifalar ro'yxatini qaytaradi"""
    return {"tasks": tasks}


@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: int):
    """Bitta vazifani id orqali olish. Agar topilmasa 404 qaytaradi"""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Vazifa (id={task_id}) topilmadi",
    )


@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(sarlavha: str, bajarildi: bool = False):
    """Yangi vazifa yaratish. Muvaffaqiyatli bo'lsa 201 qaytaradi"""
    new_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": new_id, "sarlavha": sarlavha, "bajarildi": bajarildi}
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", tags=["Tasks"])
def replace_task(task_id: int, sarlavha: str, bajarildi: bool):
    """Vazifani TO'LIQ almashtiradi — sarlavha VA bajarildi majburiy."""
    for task in tasks:
        if task["id"] == task_id:
            task["sarlavha"] = sarlavha
            task["bajarildi"] = bajarildi
            return task
    raise HTTPException(status_code=404, detail="Vazifa topilmadi")


@app.patch("/tasks/{task_id}", tags=["Tasks"])
def update_task(task_id: int, bajarildi: bool):
    """Vazifani QISMAN yangilaydi — faqat 'bajarildi' o'zgaradi."""
    for task in tasks:
        if task["id"] == task_id:
            task["bajarildi"] = bajarildi
            return task
    raise HTTPException(status_code=404, detail="Vazifa topilmadi")


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int):
    """Vazifani ro'yxatdan o'chiradi. Muvaffaqiyatli bo'lsa body qaytmaydi (204)."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return None
    raise HTTPException(status_code=404, detail="Vazifa topilmadi")
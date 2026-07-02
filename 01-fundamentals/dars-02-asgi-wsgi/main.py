"""
Dars 02 — ASGI va WSGI, sync vs async farqi
Bu darsda sync va async endpoint'lar orasidagi amaliy farqni ko'ramiz.
"""

import time
import asyncio
from fastapi import FastAPI

app = FastAPI(title="ASGI vs WSGI demo")


# SYNC endpoint — WSGI davridagi kabi yoziladi
# Bu funksiya ishlayotganda, agar u uzoq davom etsa (masalan time.sleep),
# FastAPI uni alohida thread pool'da ishga tushiradi — asosiy event loop'ni
# band qilib qo'ymaslik uchun.
@app.get("/sync-endpoint")
def sync_endpoint():
    time.sleep(2)  # 2 soniyalik "og'ir" ish simulyatsiyasi (masalan DB so'rovi)
    return {"turi": "sync", "xabar": "2 soniyadan keyin javob berdim"}


# ASYNC endpoint — ASGI'ning haqiqiy kuchi shu yerda ko'rinadi
# await bilan kutilgan vaqtda, event loop boshqa so'rovlarni qayta ishlay oladi
@app.get("/async-endpoint")
async def async_endpoint():
    await asyncio.sleep(2)  # asinxron kutish — event loop bloklanmaydi
    return {"turi": "async", "xabar": "2 soniyadan keyin javob berdim"}


# Request lifecycle'ni ko'rish uchun oddiy endpoint
@app.get("/lifecycle-demo")
async def lifecycle_demo():
    print("1. Endpoint funksiyasi ishga tushdi")
    result = {"bosqich": "endpoint ishladi, endi response qaytadi"}
    print("2. Response tayyorlanmoqda")
    return result


# Ishga tushirish: uvicorn main:app --reload
#
# SINOV: /sync-endpoint va /async-endpoint'ni Postman yoki brauzerda
# BIR VAQTDA (2 ta tab ochib) chaqiring va farqni kuzating.
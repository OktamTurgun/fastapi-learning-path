"""
Dars 02 — Mustaqil mashq

Vazifa:
1. "/server-info" manzilida GET endpoint yarating — u JSON qilib
   quyidagilarni qaytarsin:
   {
     "server": "Uvicorn",
     "protocol": "ASGI",
     "framework": "FastAPI"
   }

2. "/simulate-db-sync" — sync endpoint yarating, time.sleep(3) bilan
   "sekin DB so'rovi"ni simulyatsiya qiling, keyin natija qaytaring.

3. "/simulate-db-async" — xuddi shu ishni async va asyncio.sleep(3)
   bilan bajaring.

4. Ikkalasini alohida-alohida ishga tushirib, javob vaqtini solishtiring
   (brauzer Network tab yoki terminal orqali vaqtni kuzating).

Bonus (ixtiyoriy):
5. "/lifecycle-print" endpoint yarating — funksiya ichida kamida 3 ta
   bosqichda print() qiling (masalan "so'rov keldi", "ishlanmoqda",
   "javob tayyor") va terminalda qanday ketma-ketlikda chiqishini kuzating.
"""

from fastapi import FastAPI
import time
import asyncio

app = FastAPI(title="ASGI va WSGI demo")

# TODO: "/server-info" endpointini yozing
@app.get("/server-info")
def server_info():
  return {
    "server": "Uvicorn",
    "protocol": "ASGI",
    "framework": "FastAPI"
  }


# TODO: "/simulate-db-sync" endpointini yozing (sync, time.sleep bilan)
@app.get("/simulate-db-sync")
def simulate_db_sync():
  time.sleep(3)
  return {"turi":"sync", "xabar":"sekin DB so'rovi"}


# TODO: "/simulate-db-async" endpointini yozing (async, asyncio.sleep bilan)
@app.get("/simulate-db-async")
async def simulate_db_async():
  await asyncio.sleep(3)
  return {
    "turi":"async",
    "xabar":"sekin DB so'rovi"
  }


# TODO (bonus): "/lifecycle-print" endpointini yozing
@app.get("/lifecycle-print")
async def lifecycle_print():
  print("1. so'rov keldi")
  print("2. ishlanmoqda")
  result = {"bosqich": "javob tayyor!"}
  print("3. javob tayyor")
  return result 
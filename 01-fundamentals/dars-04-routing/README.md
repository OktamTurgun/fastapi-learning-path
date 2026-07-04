# Dars 04 — Routing (APIRouter, include_router, tags, prefix)

## 1. Muammo nimada?

Loyihangiz kattalashganda, barcha endpointlarni bitta
`main.py` faylida saqlash imkonsiz bo'lib qoladi — 50, 100, 200 ta
endpoint bitta faylda chalkashib ketadi.

**Django DRF tajribangiz bilan solishtirish:** Django'da har bir app
o'zining `urls.py` fayliga ega bo'lib, keyin asosiy `urls.py`da
`include()` orqali ular birlashtiriladi. FastAPI'da xuddi shu vazifani
**`APIRouter`** bajaradi.

## 2. APIRouter nima?

`APIRouter` — kichik, mustaqil "mini-FastAPI ilova" kabi ishlaydi. Har bir
resurs turi (users, products, orders) uchun alohida faylda alohida
`APIRouter` yaratiladi, keyin asosiy `app`ga ulanadi.

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def list_users():
    return {"users": []}
```

E'tibor bering: `@app.get(...)` o'rniga endi **`@router.get(...)`**
ishlatiladi.

## 3. include_router() — routerni asosiy ilovaga ulash

```python
# main.py
from fastapi import FastAPI
from routers import users

app = FastAPI()

app.include_router(users.router)
```

Shu qadamdan keyin `users.py`dagi barcha endpointlar asosiy `app`ning
bir qismiga aylanadi — xuddi ular `main.py`da to'g'ridan-to'g'ri
yozilgandek ishlaydi.

## 4. `prefix` — manzillarga umumiy old qo'shimcha

Har bir endpointda `/users/...` deb qayta-qayta yozish o'rniga, `prefix`
orqali buni bir marta belgilash mumkin:

```python
# routers/users.py
router = APIRouter(prefix="/users")

@router.get("/")          # haqiqiy manzil: /users/
def list_users():
    ...

@router.get("/{user_id}")  # haqiqiy manzil: /users/{user_id}
def get_user(user_id: int):
    ...
```

Yoki `prefix`ni `include_router()` chaqirilganda ham berish mumkin:

```python
app.include_router(users.router, prefix="/users")
```

**Ikkala yondashuv ham to'g'ri**, lekin ko'pchilik loyihalarda `prefix`ni
`include_router()` darajasida berish afzal ko'riladi — chunki shunda
`users.py` fayli o'zi "mustaqil" bo'lib qoladi (prefix haqida bilmaydi),
va uni istalgan prefix bilan qayta ishlatish mumkin.

## 5. `tags` — Swagger'da guruhlash

`tags` — `/docs` sahifasida endpointlarni vizual guruhlarga ajratadi
(3-darsda ko'rgan edingiz). Buni ham routerda, ham include_router'da
berish mumkin:

```python
router = APIRouter(prefix="/users", tags=["Users"])
```

yoki

```python
app.include_router(users.router, prefix="/users", tags=["Users"])
```

## 6. To'liq amaliy misol — ko'p router bilan

```python
# main.py
from fastapi import FastAPI
from routers import users, products

app = FastAPI(title="Multi-router demo")

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
```

Bu tuzilma qanchalik ko'p resurs qo'shilsa ham (`orders`, `payments`,
`categories`...), `main.py` toza va o'qilishi oson bo'lib qoladi — u
faqat routerlarni "yig'uvchi" vazifasini bajaradi.

## 7. `__init__.py` nima uchun kerak?

`routers/` papkasida `__init__.py` bo'lishi kerak — bu Python'ga bu
papka **paket (package)** ekanini bildiradi, shunda
`from routers import users` kabi import ishlaydi.

```python
# routers/__init__.py
# Bo'sh qoldirilishi mumkin, yoki qulaylik uchun:
from . import users, products
```

## 8. Nested routerlar (chuqurroq tuzilma)

Katta loyihalarda (masalan sizning Delivery API loyihangizda) routerlar
ichida yana routerlar bo'lishi mumkin:

```python
# routers/admin/__init__.py
from fastapi import APIRouter
from . import users, reports

router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(users.router)
router.include_router(reports.router)
```

Bu — Django'dagi `include()` ichida yana `include()` chaqirishga o'xshaydi.

## Xulosa

- `APIRouter` — har bir resurs uchun mustaqil "mini-app"
- `include_router()` — routerni asosiy `app`ga ulash
- `prefix` — manzil boshiga umumiy qism qo'shish (`/users`, `/products`)
- `tags` — Swagger'da vizual guruhlash
- Bu struktura loyiha kattalashganda **kodni tartibli va boshqariladigan**
  qilib saqlaydi — bu keyingi barcha modullarda (Database, Auth, va
  ayniqsa Delivery API loyihasida) asosiy ish uslubi bo'ladi
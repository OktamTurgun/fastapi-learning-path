# Dars 07 — Dependency Injection (Depends())

Bu — 1-modulning eng muhim darsi. `Depends()` FastAPI'ning "yuragi"
hisoblanadi va Authentication, Database session, Permissions kabi
deyarli barcha keyingi mavzularda asosiy vosita bo'ladi.

## 1. Dependency Injection (DI) nima?

DI — funksiyaga kerakli narsalarni **tashqaridan tayyorlab berish**
tamoyili, funksiya o'zi ularni yaratmaydi.

**Muammosiz misol orqali tushuntirish:** Aytaylik, har bir endpointda
foydalanuvchining tokenini tekshirish, DB session ochish kerak. Buni
har bir funksiya ichida qayta-qayta yozish o'rniga, buni **alohida
funksiya** qilib, FastAPI'ga "shu funksiyani ishga tushirib, natijasini
menga ber" deymiz.

## 2. Django DRF bilan solishtirish

DRF'da buni qisman **Permission classes** yoki **middleware** orqali
qilgan bo'lardingiz:

```python
# DRF uslubi (eslatma uchun)
class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
```

FastAPI'da bunga o'xshash, lekin ancha **moslashuvchan** yondashuv bor —
`Depends()` istalgan funksiyani "in'ektsiya qilish" imkonini beradi,
faqat permission emas, balki **har qanday tayyorgarlik ishini** (DB
connection, query parametrlarni guruhlash, konfiguratsiya, va h.k.)

## 3. Eng oddiy misol

```python
from fastapi import FastAPI, Depends

app = FastAPI()


def get_query_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/items")
def list_items(params: dict = Depends(get_query_params)):
    return params
```

Bu yerda `get_query_params` — bu **dependency** (bog'liqlik). FastAPI:
1. `get_query_params` funksiyasini chaqiradi
2. Uning natijasini `params` parametriga joylaydi
3. Keyin `list_items` funksiyasini ishga tushiradi

`http://.../items?skip=5&limit=20` → `{"skip": 5, "limit": 20}`

## 4. Nega bu foydali? — Kodni takrorlamaslik (DRY)

Bir nechta endpoint bir xil query parametrlarni ishlatsa:

```python
def common_params(skip: int = 0, limit: int = 10, q: str = None):
    return {"skip": skip, "limit": limit, "q": q}


@app.get("/products")
def list_products(params: dict = Depends(common_params)):
    return {"resource": "products", **params}


@app.get("/orders")
def list_orders(params: dict = Depends(common_params)):
    return {"resource": "orders", **params}
```

Ikkala endpoint ham bir xil parametr mantig'idan foydalanadi, lekin
kodni faqat bir marta yozdik.

## 5. Class-based Dependency

Funksiya o'rniga **klass** ham dependency sifatida ishlatilishi mumkin —
bu ayniqsa ko'p parametr bo'lganda o'qilishi osonroq:

```python
class CommonParams:
    def __init__(self, skip: int = 0, limit: int = 10, q: str = None):
        self.skip = skip
        self.limit = limit
        self.q = q


@app.get("/products")
def list_products(params: CommonParams = Depends(CommonParams)):
    return {"skip": params.skip, "limit": params.limit, "q": params.q}
```

## 6. Dependency ichida yana Dependency (nested)

Dependency'lar bir-birini chaqirishi mumkin — bu real loyihalarda juda
ko'p ishlatiladi (masalan: "avval DB session och, keyin shu session bilan
foydalanuvchini top, keyin foydalanuvchi orqali ruxsatni tekshir"):

```python
def get_db():
    db = "fake_db_connection"
    return db


def get_current_user(db: str = Depends(get_db)):
    # db orqali foydalanuvchini topish (hozircha demo)
    return {"id": 1, "ism": "John", "db_used": db}


@app.get("/profile")
def read_profile(user: dict = Depends(get_current_user)):
    return user
```

Bu zanjir: `read_profile` → `get_current_user` → `get_db`. FastAPI
avtomatik ravishda barcha zanjirni to'g'ri tartibda ishga tushiradi.

## 7. `yield` bilan Dependency — resurslarni tozalash (masalan DB session)

Bu naqsh Dars 12'da (SQLAlchemy) juda muhim bo'ladi:

```python
def get_db():
    db = create_connection()  # DB ulanishni ochish
    try:
        yield db  # shu yerda "to'xtaydi", endpoint ishlaydi
    finally:
        db.close()  # endpoint tugagach, ulanish yopiladi
```

`yield`dan oldingi kod — **so'rovdan oldin** ishlaydi (setup),
`finally` ichidagi kod — **so'rovdan keyin** ishlaydi (cleanup), hatto
xato yuz bergan taqdirda ham. Bu Django'dagi `context manager` yoki
`try/finally` bilan DB connection yopishga o'xshaydi, lekin FastAPI buni
avtomatlashtiradi.

## 8. Global Dependency — barcha endpointlar uchun

Agar bitta dependency **barcha** endpointlarda ishlatilishi kerak bo'lsa
(masalan har bir so'rovda API key tekshirish), uni `FastAPI()` yoki
`APIRouter()` darajasida belgilash mumkin:

```python
def verify_api_key(api_key: str = Header(...)):
    if api_key != "maxfiy-kalit":
        raise HTTPException(status_code=401, detail="Noto'g'ri API key")


app = FastAPI(dependencies=[Depends(verify_api_key)])
```

Endi **har bir** endpoint avtomatik shu tekshiruvdan o'tadi, alohida
yozish shart emas.

## 9. `Depends()` va Authentication — kelajakka ko'z tashlash

Dars 21'da (Protected Routes) siz aynan shunday narsa yozasiz:

```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token noto'g'ri")
    return user


@app.get("/me")
def read_current_user(user: dict = Depends(get_current_user)):
    return user
```

Ya'ni `Depends()` — bu butun Auth tizimingizning asosi bo'ladi. Shuning
uchun bu darsni chuqur tushunish keyingi modullarni ancha osonlashtiradi.

## Xulosa

- `Depends()` — funksiyaga tashqaridan tayyor narsa "in'ektsiya qilish"
- Asosiy foyda: **kod takrorlanmaydi** (DRY), test qilish osonlashadi
- Funksiya yoki klass — ikkalasi ham dependency bo'la oladi
- Dependency'lar bir-birini chaqirishi mumkin (nested)
- `yield` bilan — resurs ochish/yopish (DB session, fayl, va h.k.)
- `dependencies=[Depends(...)]` — global, barcha endpointlarga qo'llash
- Bu tushuncha Auth, Database, Permissions — deyarli hamma joyda ishlatiladi
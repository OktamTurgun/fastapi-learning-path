# Dars 05 — HTTP Methods (GET, POST, PUT, PATCH, DELETE)

## 1. HTTP Method nima va nega muhim?

HTTP method — client serverga **qanday amal** bajarishni so'rayotganini
bildiradi. REST arxitekturasining asosi shu — bir xil manzil (`/products`)
turli method bilan turli ma'noga ega bo'ladi.

**Django DRF bilan solishtirish:** DRF'da `ModelViewSet` ichida
`list`, `create`, `retrieve`, `update`, `destroy` metodlari bor edi —
FastAPI'da bu metodlar HTTP method'lariga to'g'ridan-to'g'ri mos keladi,
lekin siz ularni **qo'lda** yozasiz (avtomatik generatsiya bo'lmaydi,
bu ko'proq nazorat, lekin ko'proq kod degani).

## 2. Asosiy 5 ta method

| Method | Vazifasi | DRF ekvivalenti | Body bormi? |
|---|---|---|---|
| **GET** | Ma'lumot olish | `list`, `retrieve` | Yo'q |
| **POST** | Yangi resurs yaratish | `create` | Ha |
| **PUT** | Resursni **to'liq** yangilash | `update` | Ha |
| **PATCH** | Resursni **qisman** yangilash | `partial_update` | Ha |
| **DELETE** | Resursni o'chirish | `destroy` | Odatda yo'q |

## 3. GET

```python
@router.get("/products")
def list_products():
    return {"products": [...]}
```

GET — **idempotent** va **safe** bo'lishi kerak: uni necha marta
chaqirsangiz ham, serverda hech narsa o'zgarmasligi kerak (faqat o'qish).

## 4. POST — yangi resurs yaratish

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/products")
def create_product(product: dict):
    # Hozircha dict, Dars 08'dan keyin Pydantic model bo'ladi
    return {"created": product}
```

POST **idempotent emas** — bir xil so'rovni ikki marta yuborsangiz, ikkita
alohida resurs yaratiladi (masalan ikkita bir xil order).

## 5. PUT vs PATCH — eng ko'p chalkashtiriladigan farq

Bu farqni chuqur tushunish kerak, chunki ko'p junior developerlar buni
noto'g'ri ishlatadi:

- **PUT** — resursni **to'liq almashtiradi**. Agar siz faqat bitta
  maydonni yubormasangiz, qolgan maydonlar **yo'qoladi/null bo'ladi**
  (server tomonida to'liq almashtirish mantiqiga ko'ra).
- **PATCH** — faqat yuborilgan maydonlarni **qisman yangilaydi**,
  qolganlari o'zgarmasdan qoladi.

```python
@router.put("/products/{product_id}")
def replace_product(product_id: int, product: dict):
    # BUTUN resurs almashtiriladi deb hisoblanadi
    return {"id": product_id, "yangilangan": product}


@router.patch("/products/{product_id}")
def update_product(product_id: int, product: dict):
    # Faqat kelgan maydonlar yangilanadi
    return {"id": product_id, "qisman_yangilangan": product}
```

**Amaliy misol:** Agar mahsulotda `{name, price, description}` bo'lsa va
siz faqat narxni o'zgartirmoqchi bo'lsangiz:
- `PUT` bilan **barcha** maydonlarni (`name`, `price`, `description`)
  yuborishingiz kerak — aks holda `name` va `description` yo'qolishi mumkin
- `PATCH` bilan faqat `{"price": 99.00}` yuborsangiz kifoya

## 6. DELETE

```python
@router.delete("/products/{product_id}")
def delete_product(product_id: int):
    return {"message": f"{product_id} o'chirildi"}
```

DELETE odatda body qabul qilmaydi, faqat path parameter orqali qaysi
resursni o'chirishni bildiradi.

## 7. Status kodlar — nega muhim?

Har bir javob to'g'ri HTTP status kod bilan qaytishi kerak — bu
frontend/client uchun "nima bo'ldi" degan signal.

| Kod | Ma'nosi | Qachon ishlatiladi |
|---|---|---|
| **200 OK** | Muvaffaqiyatli | GET, PUT, PATCH muvaffaqiyatli bo'lganda |
| **201 Created** | Yaratildi | POST orqali yangi resurs yaratilganda |
| **204 No Content** | Muvaffaqiyatli, body yo'q | DELETE muvaffaqiyatli bo'lganda |
| **400 Bad Request** | Noto'g'ri so'rov | Client xato ma'lumot yuborganda |
| **401 Unauthorized** | Autentifikatsiya kerak | Login qilinmagan |
| **403 Forbidden** | Ruxsat yo'q | Login qilingan, lekin huquq yo'q |
| **404 Not Found** | Topilmadi | Resurs mavjud emas |
| **422 Unprocessable Entity** | Validatsiya xatosi | Pydantic validatsiyadan o'tmaganda (FastAPI avtomatik qaytaradi) |
| **500 Internal Server Error** | Server xatosi | Kutilmagan xato |

## 8. FastAPI'da status kodni belgilash

```python
from fastapi import APIRouter, status

router = APIRouter()

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: dict):
    return {"created": product}


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    return None  # 204 bilan odatda body qaytarilmaydi
```

`status.HTTP_201_CREATED` yozish `201` raqamini to'g'ridan-to'g'ri
yozishdan afzal — chunki bu o'qishni osonlashtiradi va IDE autocomplete
beradi.

## 9. Xatoni to'g'ri qaytarish — `HTTPException`

Resurs topilmasa, oddiy `{"xato": "..."}` qaytarish yetarli emas —
status kod ham 404 bo'lishi kerak:

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mahsulot topilmadi"
        )
    return product
```

**Muhim farq:** Oldingi darslarda biz `return {"xato": "..."}` deb
yozgan edik — bu **noto'g'ri odat** edi, chunki status kod baribir 200
bo'lib qolaveradi (client "hammasi joyida" deb o'ylaydi, garchi aslida
xato bo'lsa ham). `HTTPException` esa to'g'ri status kod bilan birga
xato xabarini qaytaradi. Bu haqda Dars 22'da (Exception Handling)
chuqurroq to'xtalamiz, lekin hozirdan to'g'ri odat bilan boshlash muhim.

## 10. Response — turli formatda javob qaytarish

```python
from fastapi.responses import JSONResponse, PlainTextResponse

@router.get("/matn")
def plain_text():
    return PlainTextResponse("Bu oddiy matn, JSON emas")


@router.get("/maxsus-javob")
def custom_response():
    return JSONResponse(
        status_code=201,
        content={"xabar": "Qo'lda sozlangan javob"},
        headers={"X-Custom-Header": "qiymat"},
    )
```

Odatda FastAPI avtomatik `dict`ni JSON'ga aylantiradi, lekin ba'zida
(masalan custom header qo'shish kerak bo'lganda) `JSONResponse`dan
to'g'ridan-to'g'ri foydalanish kerak bo'ladi.

## Xulosa

- GET = o'qish, POST = yaratish, PUT = to'liq yangilash,
  PATCH = qisman yangilash, DELETE = o'chirish
- Status kodlar — javobning "ma'nosi", har doim to'g'ri kodni tanlash kerak
- `HTTPException` — xatolarni to'g'ri status kod bilan qaytarish uchun
  standart yo'l (`return {"xato": ...}` emas!)
- `status.HTTP_XXX` konstantalari — raqamni yodlash o'rniga o'qilishi
  oson kod yozish uchun
# Dars 08 — Pydantic BaseModel

## 1. Nega Pydantic kerak?

Hozirgacha barcha darslarda request body sifatida oddiy `dict` yoki
alohida parametrlar (`title: str, price: float`) ishlatdik. Bu kichik
misollar uchun ishladi, lekin real loyihada muammolar tug'diradi:

- Ma'lumot strukturasi hech joyda aniq belgilanmagan
- Validatsiya qoidalarini har bir parametrga alohida yozish kerak bo'ladi
- Swagger'da to'liq schema ko'rinmaydi
- Nested (ichma-ich) ma'lumotlarni (masalan order ichida address) ifodalash qiyin

**Pydantic** — bu muammolarni hal qiladi: siz ma'lumot **shaklini**
(schema) klass sifatida belgilaysiz, Pydantic esa validatsiya, tur
konvertatsiyasi va serializatsiyani avtomatik bajaradi.

**Django DRF bilan solishtirish:** Pydantic'ning vazifasi aynan DRF'dagi
**Serializer**'ga o'xshaydi — lekin Pydantic ancha tezroq (Rust'da
yozilgan `pydantic-core` tufayli) va butun FastAPI ekotizimining
markazida turadi.

## 2. Eng oddiy BaseModel

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool
```

Bu klass endi **schema** vazifasini bajaradi. FastAPI'da endpoint
parametri sifatida ishlatilganda:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/products")
def create_product(product: Product):
    return product
```

FastAPI avtomatik ravishda:
1. Request body'ni JSON'dan `Product` obyektiga aylantiradi
2. Har bir maydonni validatsiya qiladi (`name` string bo'lishi kerak,
   `price` float, `in_stock` bool)
3. Agar validatsiya muvaffaqiyatsiz bo'lsa — **422** xato avtomatik qaytadi
4. Swagger'da to'liq schema ko'rsatiladi (`/docs`)

## 3. Validatsiya avtomatik ishlaydi

```json
// Noto'g'ri so'rov:
{
  "name": "Choynak",
  "price": "yigirma besh",
  "in_stock": true
}
```

Bu holatda FastAPI **avtomatik** 422 xato qaytaradi:

```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

Buni Django DRF'da `serializer.is_valid()` chaqirib, xatolarni qo'lda
tekshirib, `Response(serializer.errors, status=400)` deb qaytargan
bo'lardingiz — FastAPI'da bu **avtomatik**.

## 4. Ixtiyoriy maydonlar

```python
from typing import Optional
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None   # ixtiyoriy, default None
    in_stock: bool = True                # ixtiyoriy, default True
```

Agar maydonda default qiymat bo'lsa — u ixtiyoriy. Default qiymat
bo'lmasa — majburiy.

## 5. Pydantic model bilan GET, PUT, PATCH ishlatish

```python
class ProductUpdate(BaseModel):
    name: str
    price: float


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    return {"id": product_id, **product.model_dump()}
```

`.model_dump()` — Pydantic obyektini oddiy `dict`ga aylantiradi (Pydantic
v1'da bu `.dict()` deb nomlangan edi, v2'da `.model_dump()`ga o'zgardi).

## 6. Pydantic v2 — muhim metodlar

| Metod | Vazifasi |
|---|---|
| `.model_dump()` | Obyektni `dict`ga aylantirish |
| `.model_dump_json()` | Obyektni JSON string'ga aylantirish |
| `Model.model_validate(data)` | `dict`dan Pydantic obyekt yaratish |
| `Model.model_fields` | Modeldagi barcha maydonlar haqida ma'lumot |

```python
product = Product(name="Choynak", price=25.5, in_stock=True)
print(product.model_dump())        # {'name': 'Choynak', 'price': 25.5, ...}
print(product.model_dump_json())   # '{"name": "Choynak", "price": 25.5, ...}'
```

## 7. Field validatsiya — `Field()`

Dars 06'da `Query()` va `Path()` bilan validatsiya qo'shgan edik.
Pydantic modelida xuddi shunday **`Field()`** ishlatiladi:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0, description="Narx 0 dan katta bo'lishi kerak")
    quantity: int = Field(default=0, ge=0)
```

`...` — bu yerda ham "majburiy" degani (`Query`/`Path`dagi kabi).

## 8. Model ichida metod yozish mumkin

Pydantic modeli oddiy Python klassi, shuning uchun unga metod ham
qo'shish mumkin:

```python
class Product(BaseModel):
    name: str
    price: float
    discount_percent: float = 0

    def final_price(self) -> float:
        return self.price * (1 - self.discount_percent / 100)
```

```python
p = Product(name="Choynak", price=100, discount_percent=10)
print(p.final_price())  # 90.0
```

## 9. `model_config` — qo'shimcha sozlamalar (v2 uslubi)

```python
from pydantic import BaseModel, ConfigDict

class Product(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    price: float
```

`str_strip_whitespace=True` — barcha string maydonlardagi ortiqcha
bo'sh joylarni avtomatik olib tashlaydi (masalan `"  Choynak  "` →
`"Choynak"`). Bu kabi sozlamalar Dars 10'da (`Config`) chuqurroq
o'rganiladi.

## Xulosa

- `BaseModel` — request/response ma'lumot shaklini belgilash uchun
  asosiy klass
- FastAPI avtomatik validatsiya, konvertatsiya va Swagger schema
  generatsiyasini bajaradi
- `Optional[...] = None` yoki default qiymat — ixtiyoriy maydon
- `Field(...)` — qo'shimcha validatsiya qoidalari (`min_length`, `gt`, `ge`)
- `.model_dump()` — Pydantic obyektni `dict`ga aylantirish
- Bu — Django DRF'dagi Serializer'ning FastAPI'dagi analogi, lekin
  tezroq va chuqurroq FastAPI bilan integratsiyalashgan
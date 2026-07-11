# Dars 10 — Response Model, Alias, Config, Serializer

Bu — 2-modulning yakuniy darsi. Bu darsda siz **request va response
uchun turli model ishlatish**, **maydon nomlarini o'zgartirish (alias)**,
va Pydantic'ning **konfiguratsiya** imkoniyatlarini o'rganasiz.

## 1. Nega Response uchun alohida model kerak?

Hozirgacha biz bitta modelni ham request (kirish), ham response (chiqish)
uchun ishlatib keldik. Lekin real loyihada bu **xavfli**:

```python
class User(BaseModel):
    username: str
    email: EmailStr
    password: str          # <- Bu maydon RESPONSE'da ko'rinmasligi kerak!
```

Agar shu modelni response uchun ham ishlatsangiz, `password` (garchi
hash qilingan bo'lsa ham) clientga qaytarilib ketishi mumkin — bu
**jiddiy xavfsizlik xatosi**.

**Yechim:** ikkita alohida model — biri **kirish** (`UserCreate`), biri
**chiqish** (`UserResponse`) uchun:

```python
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    # password YO'Q — hech qachon qaytarilmaydi
```

## 2. `response_model` — FastAPI'ga qaysi model bilan javob berishni aytish

```python
from fastapi import FastAPI

app = FastAPI()

fake_users_db = {}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    new_user = {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "password": user.password,   # hash qilingan holda saqlanadi
    }
    fake_users_db[1] = new_user
    return new_user   # <- to'liq dict qaytarsak ham,
                       #    FastAPI faqat UserResponse maydonlarini chiqaradi!
```

**Bu FastAPI'ning kuchli xususiyati:** hatto funksiya to'liq `dict`
(parol bilan birga) qaytarsa ham, `response_model=UserResponse` tufayli
**faqat `UserResponse`da e'lon qilingan maydonlar** clientga yuboriladi.
Parol avtomatik "filtrlanadi" — buni qo'lda yozish shart emas.

**Django DRF bilan solishtirish:** Bu DRF'da ikkita alohida serializer
yozishga o'xshaydi (`UserCreateSerializer` va `UserResponseSerializer`),
lekin FastAPI'da bu ancha ixcham va deklarativ.

## 3. Alias — maydon nomini o'zgartirish

Ba'zida API tashqi dunyoga bir nomda (masalan `camelCase`, frontend
konventsiyasi) ko'rinishi kerak, lekin Python ichida boshqa nom (`snake_case`)
qulayroq. Buning uchun **`alias`** ishlatiladi:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    product_name: str = Field(..., alias="productName")
    unit_price: float = Field(..., alias="unitPrice")
```

Bu holatda request JSON'da `productName` va `unitPrice` (camelCase)
kutiladi, lekin Python kodida siz `product_name`, `unit_price`
(snake_case) bilan ishlaysiz:

```json
{
  "productName": "Choynak",
  "unitPrice": 25.5
}
```

**Muhim:** Default holatda, agar `alias` ishlatilsa, faqat **alias nomi**
bilan ma'lumot qabul qilinadi (`product_name` deb yuborsangiz, xato
chiqadi). Buni o'zgartirish uchun `populate_by_name=True` kerak.

## 4. `model_config` — `populate_by_name`

```python
from pydantic import BaseModel, Field, ConfigDict

class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_name: str = Field(..., alias="productName")
    unit_price: float = Field(..., alias="unitPrice")
```

Bu bilan endi ham `productName`, ham `product_name` orqali ma'lumot
yuborish mumkin bo'ladi — bu moslashuvchanlik uchun foydali.

## 5. Response'da alias bilan qaytarish — `by_alias=True`

```python
product = Product(product_name="Choynak", unit_price=25.5)
print(product.model_dump(by_alias=True))
# {'productName': 'Choynak', 'unitPrice': 25.5}

print(product.model_dump())
# {'product_name': 'Choynak', 'unit_price': 25.5}   <- alias'siz
```

FastAPI endpoint darajasida ham buni sozlash mumkin:

```python
@app.get("/products/{id}", response_model=Product, response_model_by_alias=True)
def get_product(id: int):
    ...
```

## 6. `model_config` — boshqa foydali sozlamalar

```python
from pydantic import BaseModel, ConfigDict

class Product(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,   # "  Choynak  " -> "Choynak"
        str_to_lower=True,            # "CHOYNAK" -> "choynak"
        extra="forbid",               # noma'lum maydon kelsa — xato beradi
    )

    name: str
    price: float
```

`extra="forbid"` ayniqsa muhim — default holatda (`extra="ignore"`)
Pydantic ortiqcha maydonlarni jim o'tkazib yuboradi, lekin `"forbid"`
bilan, agar client kutilmagan maydon yuborsa (masalan xato yozilgan
maydon nomi), Pydantic **422 xato** qaytaradi — bu xatoni erta aniqlashga
yordam beradi.

## 7. `response_model_exclude_unset` — faqat berilgan maydonlarni qaytarish

PATCH so'rovlarida foydali — faqat client yuborgan maydonlarni qaytarish:

```python
@app.patch("/products/{id}", response_model=Product, response_model_exclude_unset=True)
def update_product(id: int, product: ProductUpdate):
    ...
```

## 8. Computed field — hisoblangan maydon (Pydantic v2)

Ba'zida response'da modelda yo'q, lekin **hisoblab chiqariladigan**
maydon kerak bo'ladi:

```python
from pydantic import BaseModel, computed_field

class Product(BaseModel):
    price: float
    quantity: int

    @computed_field
    @property
    def total_value(self) -> float:
        return self.price * self.quantity
```

Bu — Dars 08/09'da yozgan oddiy `total_value()` metodidan farqli:
`@computed_field` bilan bu maydon **avtomatik ravishda** `.model_dump()`
va API response'ida ham ko'rinadi, alohida chaqirish shart emas.

## 9. To'liq amaliy misol

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict, computed_field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # DB obyektidan o'qish uchun (Dars 12'da kerak bo'ladi)

    id: int
    username: str
    email: EmailStr
    # password yo'q!


class ProductResponse(BaseModel):
    id: int
    name: str = Field(..., alias="productName")
    price: float
    quantity: int

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def total_value(self) -> float:
        return self.price * self.quantity
```

`from_attributes=True` — bu ayniqsa muhim, chunki Dars 12'dan boshlab
siz SQLAlchemy modellaridan (oddiy `dict` emas, balki ORM obyektlaridan)
Pydantic response yaratasiz — bu sozlama shuni imkon qiladi.

## Xulosa

- **Request va Response uchun alohida model** — xavfsizlik va aniqlik
  uchun standart amaliyot (masalan parolni response'da ko'rsatmaslik)
- `response_model=...` — FastAPI'ga qaysi maydonlarni chiqarishni aytadi,
  ortiqcha ma'lumotni avtomatik filtrlaydi
- `alias` — tashqi (JSON) va ichki (Python) nomlash farqini boshqarish
  uchun (`camelCase` vs `snake_case`)
- `ConfigDict(populate_by_name=True)` — ham original, ham alias nom bilan
  qabul qilish
- `ConfigDict(extra="forbid")` — kutilmagan maydonlarni rad etish
- `@computed_field` — response'da avtomatik hisoblanadigan maydon
- `from_attributes=True` — ORM obyektlaridan Pydantic model yaratish
  uchun (Database modulida asosiy vosita bo'ladi)
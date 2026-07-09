# Dars 09 — Nested Models, List, Optional, EmailStr

## 1. Nested Model nima?

Real loyihalarda ma'lumotlar deyarli hech qachon "tekis" (flat) bo'lmaydi.
Masalan, buyurtma (`Order`) ichida mijoz (`Customer`) ma'lumoti, mijoz
ichida manzil (`Address`) ma'lumoti bo'lishi mumkin. Pydantic'da bir
modelni boshqa model ichida ishlatish — **Nested Model** deb ataladi.

```python
from pydantic import BaseModel

class Address(BaseModel):
    city: str
    street: str
    zip_code: str


class Customer(BaseModel):
    name: str
    address: Address    # <- Nested model!
```

Request JSON shunday ko'rinadi:

```json
{
  "name": "Botir",
  "address": {
    "city": "Tashkent",
    "street": "Amir Temur ko'chasi",
    "zip_code": "100000"
  }
}
```

FastAPI/Pydantic bu ichma-ich strukturani **avtomatik** validatsiya
qiladi — `address` ichidagi har bir maydon ham tekshiriladi.

**Django DRF bilan solishtirish:** Bu — DRF'dagi **nested serializer**
bilan bir xil g'oya (`class AddressSerializer` ni `CustomerSerializer`
ichida `address = AddressSerializer()` deb ishlatgan bo'lardingiz).

## 2. List — ro'yxat turidagi maydonlar

Agar bitta modelda **bir nechta** boshqa model bo'lishi kerak bo'lsa
(masalan buyurtma ichida bir nechta mahsulot), `List[...]` ishlatiladi:

```python
from typing import List
from pydantic import BaseModel


class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float


class Order(BaseModel):
    customer_name: str
    items: List[OrderItem]    # <- bir nechta OrderItem
```

```json
{
  "customer_name": "Dilnoza",
  "items": [
    {"product_name": "Choynak", "quantity": 2, "price": 25.5},
    {"product_name": "Piyola", "quantity": 6, "price": 5.0}
  ]
}
```

**Python 3.9+ uslubi:** `List[OrderItem]` o'rniga to'g'ridan-to'g'ri
`list[OrderItem]` ham yozish mumkin (kichik harf bilan, `typing`dan
import qilmasdan) — ikkalasi ham ishlaydi, lekin ko'p loyihalarda hali
ham `typing.List` ko'rinadi (eski kod bilan moslik uchun).

## 3. Optional — ixtiyoriy nested model

```python
from typing import Optional

class Customer(BaseModel):
    name: str
    address: Optional[Address] = None    # manzil berilishi shart emas
```

## 4. EmailStr — email validatsiyasi

Oddiy `str` bilan email formatini tekshirish uchun qo'lda regex yozish
kerak bo'lardi. Pydantic buning uchun tayyor tur beradi:

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
```

Agar `email` noto'g'ri formatda kelsa (masalan `"email emas"`),
Pydantic **avtomatik** 422 xato qaytaradi — email regex'ini qo'lda
yozish shart emas.

**O'rnatish:** `EmailStr` ishlashi uchun qo'shimcha paket kerak:
```bash
pip install pydantic[email]
```

## 5. To'liq amaliy misol — Order + Customer + Items

```python
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class Address(BaseModel):
    city: str
    street: str
    zip_code: Optional[str] = None


class Customer(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    address: Optional[Address] = None


class OrderItem(BaseModel):
    product_name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)


class Order(BaseModel):
    customer: Customer
    items: List[OrderItem]

    def total_price(self) -> float:
        return sum(item.quantity * item.price for item in self.items)
```

```json
{
  "customer": {
    "name": "Botir",
    "email": "botir@example.com",
    "address": {
      "city": "Tashkent",
      "street": "Chilonzor"
    }
  },
  "items": [
    {"product_name": "Choynak", "quantity": 2, "price": 25.5},
    {"product_name": "Piyola", "quantity": 6, "price": 5.0}
  ]
}
```

## 6. Nested model bilan ishlashda muhim narsa — `.model_dump()`

```python
order = Order(**request_data)
print(order.model_dump())
```

`.model_dump()` **butun nested strukturani** ham `dict`ga aylantiradi —
`customer.address` ham avtomatik ichki `dict`ga o'giriladi. Bu real
loyihada DB'ga yozish yoki JSON qaytarish uchun juda qulay.

## 7. List ichida oddiy turlar (nested model emas)

`List` faqat model uchun emas, oddiy turlar uchun ham ishlatiladi:

```python
class Product(BaseModel):
    name: str
    tags: List[str] = []          # ["fantastika", "bestseller"]
    related_ids: List[int] = []   # [3, 7, 12]
```

## 8. Swagger'da nested model qanday ko'rinadi

`/docs` sahifasida nested model ishlatilganda, Swagger avtomatik
**"Schema"** bo'limida ichma-ich strukturani chizib ko'rsatadi — bu
frontend developerlar uchun API'ni tushunishni ancha osonlashtiradi
(masalan sizning marionettes.uz'dagi React frontend integratsiyasida
ayni shu schema orqali qaysi maydonlar kerakligini ko'rish mumkin bo'ladi).

## Xulosa

- **Nested Model** — bir Pydantic modelni boshqasi ichida ishlatish
  (masalan `Customer` ichida `Address`)
- **List[Model]** — bir nechta obyektdan iborat ro'yxat (masalan
  `Order` ichida bir nechta `OrderItem`)
- **Optional[Model] = None** — ixtiyoriy nested model
- **EmailStr** — email formatini avtomatik tekshiradigan maxsus tur
  (`pip install pydantic[email]` kerak)
- Bu tushunchalar sizning real loyihalaringizda (Storely, Delivery API)
  order/customer/product munosabatlarini ifodalashda asosiy vosita bo'ladi
# Dars 23 — Service Layer (Storely)

Hozirgacha strukturangiz shunday edi:

Router → CRUD → Database

Bu — kichik loyihalar uchun yetarli. Lekin biznes-mantiq murakkablashsa
(masalan "mahsulot qo'shishda, agar kategoriya faol bo'lmasa xato
berish", yoki "buyurtma yaratishda, mijozning balansini tekshirish va
kamaytirish") — bu mantiqni **routerga yozish noto'g'ri** (router faqat
HTTP bilan shug'ullanishi kerak) va **CRUD'ga yozish ham noto'g'ri**
(CRUD faqat DB bilan ishlashi kerak, "toza" qolishi kerak).

## 1. Service Layer nima?

**Service Layer** — biznes-mantiqni joylashtiradigan oraliq qatlam:

Router (HTTP) → Service (biznes-mantiq) → CRUD (DB so'rovlar) → Database

**Django solishtirma:** Bu — Django loyihalarida ko'pincha
`services.py` yoki "fat models, thin views" tamoyilining muqobili
sifatida ishlatiladigan pattern. DRF'da buni ko'pincha
`serializer.save()` ichida yoki alohida `services/` papkasida
yozishadi.

## 2. Nima uchun bu farq muhim? (aniq misol bilan)

**Muammo:** Mahsulot yaratishda, kategoriya mavjudligini tekshirish
kerak. Buni qayerga yozish kerak?

- **CRUD'da emas** — CRUD faqat "yozish/o'qish" bilan shug'ullanadi,
  qaror qabul qilmaydi
- **Routerda emas** — router HTTP so'rov/javobni boshqaradi, biznes
  qoidalarni bilishi shart emas
- **Service'da** — aynan shu yerda: "mahsulot yaratishdan oldin
  kategoriya borligini tekshir, bo'lmasa xato ber, bo'lsa CRUD orqali
  yarat"

## 3. `services/product_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.crud import product as crud_product
from app.crud import category as crud_category


class ProductService:
    """Product bilan bog'liq barcha biznes-mantiq shu yerda joylashadi"""

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        # Biznes qoida: kategoriya mavjud bo'lishi shart
        category = await crud_category.get_category(db, product_data.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist",
            )

        return await crud_product.create_product(db, product_data)

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: int, product_data: ProductUpdate
    ) -> Product:
        # Biznes qoida: agar category_id yangilansa, u ham mavjud bo'lishi kerak
        if product_data.category_id is not None:
            category = await crud_category.get_category(db, product_data.category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with id {product_data.category_id} does not exist",
                )

        updated = await crud_product.update_product(db, product_id, product_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        return updated

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> None:
        success = await crud_product.delete_product(db, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
```

**Nima o'zgardi?** E'tibor bering — **404/400 xatoларni router o'rniga
endi Service qaytaryapti**. Bu — muhim arxitektura qarori: xatoni "kim
aniqlaydi" (Service — biznes qoida asosida) va "kim HTTP'ga
aylantiradi" (`HTTPException` — bu FastAPI'ning o'zi HTTP javobiga
aylantiradi, shuning uchun Service ichida ham ishlatish qulay).

## 4. Router — endi yupqa (thin), faqat Service'ga murojaat qiladi

```python
# app/routers/product.py — yangilanadi
from app.services.product_service import ProductService

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await ProductService.create_product(db, product)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    return await ProductService.update_product(db, product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    await ProductService.delete_product(db, product_id)
```

**E'tibor bering:** Router endi `HTTPException`larni o'zi tashlamaydi
— bu vazifa endi **to'liq Service'ga o'tgan**. Router faqat: (1) HTTP
so'rovni qabul qiladi, (2) Service'ga uzatadi, (3) natijani qaytaradi.

## 5. Nega `@staticmethod`?

`ProductService`da barcha metodlar `@staticmethod` — chunki bu klass
**hech qanday holatni (state) saqlamaydi**, faqat funksiyalarni
mantiqiy guruhlash uchun ishlatiladi (Python'da "namespace" sifatida).
Muqobil sifatida, oddiy modul darajasidagi funksiyalar (`class`siz)
ham ishlatilishi mumkin — ikkalasi ham keng tarqalgan, bu — uslub
tanlovi.

## 6. Qachon Service Layer kerak, qachon ortiqcha?

**Kerak, agar:**
- Bir nechta CRUD chaqiruvi birlashtirilishi kerak bo'lsa (masalan
  "kategoriya borligini tekshirish + mahsulot yaratish")
- Tranzaksiya boshqaruvi kerak bo'lsa (bir nechta amal — yoki hammasi
  muvaffaqiyatli, yoki hech biri)
- Bir xil mantiq bir nechta joyda (masalan turli routerlardan) chaqirilishi kerak bo'lsa

**Ortiqcha, agar:**
- Oddiy CRUD (faqat yaratish/o'qish/o'zgartirish/o'chirish, hech qanday
  qo'shimcha tekshiruv) — bunday holda Service qatlami faqat CRUD'ni
  "qayta chaqiradi", hech qanday qiymat qo'shmaydi

Bizning holatda, `Category` uchun Service **shart emas** (oddiy CRUD),
lekin `Product` uchun kerak (kategoriya bog'liqligi tufayli).

## Xulosa

- **Service Layer** — Router va CRUD orasidagi biznes-mantiq qatlami
- **Router** — faqat HTTP bilan ishlaydi, "yupqa" bo'lishi kerak
- **CRUD** — faqat DB bilan ishlaydi, biznes qoidalarni bilmaydi
- **Service** — bu ikkisini bog'lovchi, qarorlar qabul qiluvchi qatlam
- Har doim ham Service kerak emas — faqat murakkablik paydo bo'lganda

## Amaliy struktura

```
dars-23-service-layer/
├── README.md
├── ...
└── app/
    ├── services/                  <- YANGI papka
    │   ├── __init__.py
    │   └── product_service.py
    └── routers/
        └── product.py               <- YANGILANADI (Service orqali)
```

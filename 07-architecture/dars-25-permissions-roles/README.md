# Dars 25 — Permissions & Roles (Storely)

Hozirgacha autentifikatsiya (Dars 19-21) bizga faqat bitta savolga
javob berdi: **"Bu foydalanuvchi kim?"** (token orqali). Lekin haqiqiy
loyihalarda ikkinchi savol ham bor: **"Bu foydalanuvchi shu amalni
bajarishga huquqi bormi?"** — bu, aynan, **avtorizatsiya
(authorization)**, va bugungi dars shu haqida.

## 1. Authentication vs Authorization — farqni aniqlashtiramiz

| | Savol | Dars |
|---|---|---|
| **Authentication** | "Siz kimsiz?" | Dars 19-21 (JWT, login, protected routes) |
| **Authorization** | "Sizga bu ruxsat berilganmi?" | Dars 25 (bugun) |

**Django solishtirma:** Bu — aynan Django'dagi `permissions.py` yoki
DRF'dagi `IsAdminUser`, `IsAuthenticated`, custom `BasePermission`
klasslari bilan bir xil g'oya. FastAPI'da bunday tayyor tizim yo'q —
Dependency Injection orqali o'zimiz quramiz.

## 2. Muammo — hozircha har qanday login qilgan user hamma narsani qila oladi

Dars 21'da yozgan `get_current_active_user` faqat "token to'g'rimi,
user faolmi" tekshiradi — lekin masalan, oddiy mijoz (customer) ham
boshqa birovning buyurtmasini o'chira oladi, yoki yangi mahsulot qo'sha
oladi. Bu — xavfsizlik nuqtai nazaridan noto'g'ri.

Kerak bo'lgan narsa: **rol tizimi** — masalan `admin`, `manager`,
`customer` — va har bir endpoint "faqat shu rollarga ruxsat" deb
belgilay olishi.

## 3. `User` modeliga `role` maydonini qo'shish

```python
# app/models/user.py — yangilanadi
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)  # <- YANGI

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
```

**Muhim:** `role` ustuni qo'shilgani uchun **Alembic migratsiyasi kerak
bo'ladi** (Dars 14'dagi kabi):

```powershell
alembic revision --autogenerate -m "add role to users"
alembic upgrade head
```

`str, enum.Enum`dan meros olish — bu Python'ning standart usuli,
`UserRole.ADMIN == "admin"` solishtirishni ham to'g'ridan-to'g'ri
ishlatish imkonini beradi.

## 4. Permission dependency — `require_role`

Bu — bugungi darsning yuragi. Dars 21'dagi `get_current_active_user`
ustiga, **parametrlashtirilgan** dependency quramiz:

```python
# app/core/dependencies.py — qo'shiladi
from typing import List
from app.models.user import User, UserRole


def require_role(*allowed_roles: UserRole):
    """
    Factory function — ruxsat berilgan rollar ro'yxatini qabul qiladi
    va shu rollarni tekshiradigan dependency function qaytaradi.

    Ishlatilishi: Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu amal uchun ruxsat yo'q. Talab qilinadi: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker
```

**Bu nima uchun "factory function"?** `require_role` o'zi dependency
emas — u **dependency yaratadigan funksiya**. Chaqirilganda
(`require_role(UserRole.ADMIN)`), ichki `role_checker` funksiyasini
qaytaradi, va aynan o'sha ichki funksiya `Depends(...)` ichida
ishlatiladi. Bu naqsh — Python'da **closure** deb ataladi
(`role_checker` o'zining tashqi qatlamidagi `allowed_roles`ni "eslab
qoladi").

**401 va 403 farqi:** `get_current_active_user` token yo'q/noto'g'ri
bo'lsa `401 Unauthorized` beradi ("siz kimligingiz noaniq").
`require_role` esa token to'g'ri, lekin rol yetarli emas bo'lsa `403
Forbidden` beradi ("siz kimligingiz aniq, lekin ruxsat yo'q"). Bu
ikkovi ko'pincha chalkashtiriladi, lekin HTTP semantikasi bo'yicha
aniq farq bor.

## 5. Router'da ishlatish

```python
# app/routers/product.py — yangilanadi
from app.core.dependencies import require_role
from app.models.user import UserRole


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),  # <- faqat admin
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product(product_id)
```

E'tibor bering: `create_product` uchun `ADMIN` **yoki** `MANAGER`
ruxsat etiladi, `delete_product` uchun faqat `ADMIN`. Bu — real
loyihalarda odatiy holat: yaratish kengroq doiraga, o'chirish tor
doiraga ruxsat etiladi.

## 6. "O'zining ma'lumotiga ega bo'lish" qoidasi (object-level permission)

Rol tekshiruvi yetarli emas holatlar ham bor — masalan, `Customer`
faqat **o'zining** buyurtmasini ko'ra olishi, boshqa mijozning
buyurtmasini emas. Bu — **object-level permission**, va Service
qatlamida tekshiriladi (chunki bu ma'lum bir obyektga bog'liq, umumiy
rolga emas):

```python
# app/services/order_service.py — qo'shiladi
class OrderService:
    # ...

    async def get_order_for_user(self, order_id: int, current_user: User) -> Order:
        order = await self.order_repo.get(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Buyurtma topilmadi")

        # ADMIN va MANAGER — hamma narsani ko'radi
        if current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
            return order

        # CUSTOMER — faqat o'zining buyurtmasini
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu buyurtma sizga tegishli emas",
            )
        return order
```

**Diqqat:** bu yerda `current_user.id != order.customer_id`
solishtiruvi ishlashi uchun, aslida `Customer` va `User` orasida
bog'liqlik bo'lishi kerak (masalan `Customer.user_id` orqali).
Storely'da hozircha `Customer` va `User` alohida modellar — bu,
ehtimol, keyingi darsda (yoki mustaqil kengaytirish sifatida)
`Customer.user_id = ForeignKey("users.id")` qo'shishni talab qilishi
mumkin. Hozircha tushunchani tushunish uchun soddalashtirilgan holat
sifatida qoldiramiz.

## 7. Django bilan solishtirma — nima farq qiladi

DRF'da xuddi shunga o'xshash narsa `permission_classes =
[IsAdminUser]` yoki custom `BasePermission` orqali
`has_permission`/`has_object_permission` metodlarida yoziladi.
FastAPI'da farq shundaki — **hamma narsa Dependency Injection
orqali**, alohida "permission klassi" tushunchasi yo'q, oddiy function
bo'lib qoladi. Bu — kamroq "sehr" (magic), ko'proq oshkora (explicit)
— FastAPI falsafasining o'ziga xos tomoni.

## Xulosa

- **Authentication** ("kimsiz?") va **Authorization** ("ruxsatingiz
  bormi?") — ikki xil narsa
- **`role`** ustuni `User` modeliga qo'shiladi (`Enum` orqali)
- **`require_role(*roles)`** — factory function, parametrlashtirilgan
  dependency yaratadi
- **`401`** — token yo'q/noto'g'ri; **`403`** — token to'g'ri, lekin
  ruxsat yetarli emas
- **Object-level permission** — Service qatlamida, "bu aniq obyekt
  shu userga tegishlimi" tekshiruvi

## Amaliy struktura

```
dars-25-permissions-roles/
├── README.md
└── app/
    ├── models/
    │   └── user.py                <- YANGILANADI (role ustuni)
    ├── core/
    │   └── dependencies.py         <- YANGILANADI (require_role qo'shiladi)
    ├── services/
    │   └── order_service.py        <- YANGILANADI (get_order_for_user)
    ├── routers/
    │   ├── product.py               <- YANGILANADI (require_role bilan)
    │   └── order.py                 <- YANGILANADI
    └── alembic/versions/
        └── xxxx_add_role_to_users.py   <- YANGI migratsiya
```
# Dars 11 — Config, .env, BaseSettings, Project Structure

Bu — 3-modulning yagona, lekin juda muhim darsi. Bu yerda siz keyingi
barcha modullarda ishlatiladigan **professional loyiha strukturasini**
va **konfiguratsiya boshqaruvini** o'rganasiz.

## 1. Nega bitta `main.py` yetarli emas?

Hozirgacha har bir dars alohida, mustaqil `main.py` faylida edi. Lekin
haqiqiy loyiha (masalan sizning marionettes.uz yoki Storely) kattalashgan
sayin:

- Routerlar ko'payadi (Dars 04'da ko'rganingizdek)
- Pydantic modellar ko'payadi
- Database bilan ishlash kerak bo'ladi
- Maxfiy ma'lumotlar (DB parol, JWT secret, API kalitlar) boshqarilishi kerak

Buning uchun **standart Python loyiha strukturasi** kerak.

## 2. Tavsiya etilgan struktura

"""
Dars 10 — Mustaqil mashq: Storely — Xodim (Employee) tizimi

Vazifa:

1. `EmployeeCreate` modelini yarating (request uchun):
   - full_name: str, min_length=2
   - email: EmailStr
   - salary: float, gt=0
   - pin_code: str, min_length=4   (bu maydon response'da KO'RINMASLIGI kerak!)

pasted# exercise.pyYaxshi urinish — asosiy g'oyalar (response_model, alias, computed_field) to'g'ri qo'llanilgan. Lekin 2 ta xato bor, ulardan biri kod ishlamay qoladigan darajada.
🔴 Kritik xato — computed_field ichida noto'g'ri atribut nomlari
python@computed_field
@property
def total_value(self) -> float:
    return round(self.price * self.quantity, 2)   # ❌ "price" va "quantity" bu modelda yo'q!
InventoryItemResponse modelida maydonlar unit_cost va stock_count deb nomlangan, price/quantity emas. Bu AttributeError beradi — GET /inventory/{item_id} chaqirilganda server 500 xato qaytaradi, chunki self.price mavjud emas.
Tuzatish:
python@computed_field
@property
def total_value(self) -> float:
    return round(self.unit_cost * self.stock_count, 2)
Shuningdek, vazifada bu maydon nomi total_cost deb so'ralgan edi, siz total_value deb yozibsiz — funksional emas, lekin spec'ga rioya qilish odatini eslatib qo'yaman.
🟡 Muhim kamchilik — EmployeeResponseda full_name yo'q
pythonclass EmployeeResponse(BaseModel):
    id: int
    email: EmailStr
    salary: float
    # full_name yo'q!
Vazifada aniq ko'rsatilgan edi: EmployeeResponse da full_name bo'lishi kerak (faqat pin_code chiqarilmasligi kerak edi, full_name emas). Hozirgi holatda full_name ham pin_code kabi "yo'qolib" ketyapti — bu xato, chunki full_name maxfiy ma'lumot emas, uni ko'rsatish kerak.
Tuzatish:
pythonclass EmployeeResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    salary: float
To'liq tuzatilgan versiya (faqat o'zgargan qismlar)
pythonclass EmployeeResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    salary: float


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: int
    item_name: str = Field(..., alias="itemName")
    unit_cost: float = Field(..., alias="unitCost")
    stock_count: int = Field(..., alias="stockCount")

    @computed_field
    @property
    def total_cost(self) -> float:
        return round(self.unit_cost * self.stock_count, 2)
Yaxshi bajarilgan qismlar

EmployeeCreate — to'liq to'g'ri, barcha validatsiya qoidalari joyida
POST/GET endpointlar — response_model to'g'ri ishlatilgan, xatolik ishlash mantig'i (404) to'g'ri
pin_codeni hash qilib saqlash g'oyasi (f"hashed_{...}") — real loyihadagi (bcrypt) mantiqqa to'g'ri yaqinlashtirilgan
populate_by_name=True to'g'ri qo'yilgan

Sinash
powershellpython -m uvicorn exercise:app --reload --port 8008
Tekshiring:

POST /employees — javobda full_name ko'rinishi, pin_code ko'rinmasligi kerak
GET /inventory/1 — itemName, unitCost, stockCount (camelCase) va total_cost to'g'ri hisoblanganini tekshiring

Commit
powershellgit add 02-pydantic/dars-10-response-model
git commit -m "docs(dars-10): Response Model, Alias, Config, computed_field"
git push
2-Modul (Pydantic) yakunlandi! 🎉
Tuzatib tasdiqlagach, root README.mdni yangilang:
powershellgit add README.md
git commit -m "docs: 2-modul (Pydantic) yakunlandi"
git push
Tayyor bo'lganda 3-Modul — Project Setup (Dars 11: Config, .env, BaseSettings) ga o'tamiz.http://127.0.0.1:8008/employees{"detail":"Method Not Allowed"}Diagnosed endpoint mismatch causing method restriction errorDiagnosed endpoint mismatch causing method restriction errorBu — xato emas, balki kutilgan natija! Sizning exercise.py faylingizda /employees manzili uchun faqat POST metodi yozilgan, GET metodi umuman yo'q:
python@app.post("/employees", ...)   # faqat shu bor
def create_employee(employee: EmployeeCreate):
    ...

@app.get("/employees/{employee_id}", ...)   # bu ID bilan, ro'yxat emas
def get_employee(employee_id: int):
    ...
Ya'ni /employees (ID'siz) uchun GET so'rov yuborsangiz, FastAPI "bu manzilda GET metodi ro'yxatga olinmagan" deb 405 xato qaytaradi — bu to'g'ri xatti-harakat, chunki vazifada bunday endpoint so'ralmagan edi.
Agar hammasi to'g'ri ishlayotganini tekshirmoqchi bo'lsangiz
1. POST bilan xodim qo'shing (/docs orqali yoki curl bilan):
powershellcurl -X POST http://127.0.0.1:8008/employees `
  -H "Content-Type: application/json" `
  -d '{\"full_name\": \"Aziza Karimova\", \"email\": \"aziza@storely.uz\", \"salary\": 4500000, \"pin_code\": \"1234\"}'
Yoki eng qulaysi — /docs sahifasini oching, POST /employees ni toping, "Try it out" tugmasini bosing, test JSON'ni kiritib, "Execute" qiling.
2. Keyin ID orqali oling:
http://127.0.0.1:8008/employees/1
Bu ishlashi kerak, chunki bu manzil aniq belgilangan.
Agar ro'yxatni ham ko'rmoqchi bo'lsangiz (ixtiyoriy qo'shimcha)
Bu vazifada so'ralmagan, lekin amaliyot uchun qo'shib ko'rishingiz mumkin:
python@app.get("/employees", response_model=list[EmployeeResponse], tags=["Employees"])
def list_employees():
    return employees_db

Avval /docs orqali POST qilib, keyin GET /employees/1 bilan tekshirib ko'ring — natijani ayting.http://127.0.0.1:8008/employees/1{
  "id": 1,
  "full_name": "Olim Salim",
  "email": "olim@example.com",
  "salary": 1200000
}Zo'r! 🎉 Bu — aynan kutilgan natija. Diqqat qiling:

✅ full_name ko'rinyapti (avvalgi xato tuzatilgach)
✅ pin_code hech qayerda yo'q — xavfsizlik talabi to'liq bajarilgan
✅ response_model=EmployeeResponse to'g'ri ishlayapti — hatto create_employee funksiyasi to'liq dict (pin_code bilan birga) qaytargan bo'lsa ham, FastAPI faqat EmployeeResponseda e'lon qilingan maydonlarni chiqardi

Bu — real loyihalarda (masalan sizning EduCore CRM'dagi JWT auth tizimingizda) parolni/PIN kodni hech qachon API javobida ko'rsatmaslik uchun ishlatiladigan aynan shu naqsh.
Endi qolganini ham tekshiring
http://127.0.0.1:8008/inventory/1
http://127.0.0.1:8008/inventory/2
Bu yerda tekshiring:

itemName, unitCost, stockCount — camelCase (alias) ko'rinishida chiqishi kerak
total_cost — unit_cost * stock_count to'g'ri hisoblangan bo'lishi kerak

Agar computed_fielddagi xatoni (avvalgi javobimda ko'rsatgan self.price/self.quantity → self.unit_cost/self.stock_count) hali tuzatmagan bo'lsangiz, bu yerda 500 Internal Server Error chiqadi. Tuzatib, qayta sinab ko'ring.
Commit
Hammasi to'g'ri ishlagach:
powershellgit add 02-pydantic/dars-10-response-model
git commit -m "docs(dars-10): Response Model, Alias, Config, computed_field"
git push
2-Modul yakunlandi
powershellgit add README.md
git commit -m "docs: 2-modul (Pydantic) yakunlandi"
git push

/inventory/{id} natijasini menga tashlang — tasdiqlagach, 3-Modul — Project Setup (Dars 11: Config, .env, BaseSettings) ga o'tamiz, bu yerda loyihangizni professional tarzda tashkil qilishni o'rganasiz (bu keyingi barcha modullar — Database, Auth — uchun poydevor bo'ladi).3-Modul — Project Setup (Dars 11: Config, .env, BaseSettings) ga o'tamiz, bu yerda loyihangizni professional tarzda tashkil qilishni o'rganasiz (bu keyingi barcha modullar — Database, Auth — uchun poydevor bo'ladi).Architected comprehensive project structure lesson with folder organizationArchitected comprehensive project structure lesson with folder organization📁 Yaratish kerak: 03-project-setup/dars-11-config-structure/
powershellmkdir 03-project-setup\dars-11-config-structure
cd 03-project-setup\dars-11-config-structure
Eslatma: Bu darsda yangi kutubxona kerak bo'ladi:
powershellpip install pydantic-settings
pip freeze > ..\..\requirements.txt
Bu dars boshqalardan farqli — bitta fayl emas, balki to'liq professional loyiha strukturasi yaratamiz. Bu struktura Dars 12'dan boshlab (Database, Auth, va hatto Delivery API'gacha) asos bo'lib xizmat qiladi.

📄 README.md — Nazariya
markdown# Dars 11 — Config, .env, BaseSettings, Project Structure

Bu — 3-modulning yagona, lekin juda muhim darsi. Bu yerda siz keyingi
barcha modullarda ishlatiladigan **professional loyiha strukturasini**
va **konfiguratsiya boshqaruvini** o'rganasiz.

## 1. Nega bitta `main.py` yetarli emas?

Hozirgacha har bir dars alohida, mustaqil `main.py` faylida edi. Lekin
haqiqiy loyiha (masalan sizning marionettes.uz yoki Storely) kattalashgan
sayin:

- Routerlar ko'payadi (Dars 04'da ko'rganingizdek)
- Pydantic modellar ko'payadi
- Database bilan ishlash kerak bo'ladi
- Maxfiy ma'lumotlar (DB parol, JWT secret, API kalitlar) boshqarilishi kerak

Buning uchun **standart Python loyiha strukturasi** kerak.

## 2. Tavsiya etilgan struktura

myproject/
├── app/
│   ├── init.py
│   ├── main.py              # FastAPI() shu yerda, routerlarni yig'adi
│   ├── config.py            # Barcha sozlamalar (BaseSettings)
│   ├── routers/
│   │   ├── init.py
│   │   ├── users.py
│   │   └── products.py
│   ├── models/               # Pydantic modellar (Dars 12'dan keyin DB modellar ham)
│   │   ├── init.py
│   │   └── user.py
│   ├── schemas/               # Ba'zi loyihalarda models/schemas alohida
│   ├── services/              # Biznes-logika (Dars 23'da chuqurroq)
│   └── database.py            # DB connection (Dars 12'da qo'shiladi)
├── .env                        # Maxfiy o'zgaruvchilar (Git'ga QO'SHILMAYDI!)
├── .env.example                # .env namunasi (Git'ga qo'shiladi)
├── .gitignore
├── requirements.txt
└── README.md

**Muhim farq:** Bu struktura sizning oldingi darslaringizdagi
`routers/` papkasiga o'xshaydi (Dars 04), lekin endi hammasi **`app/`**
degan bitta paket ichiga joylashadi — bu Python'da katta loyihalarni
tashkil qilishning standart usuli.

## 3. `.env` fayli nima uchun kerak?

Maxfiy yoki muhitga bog'liq ma'lumotlarni (DB parol, JWT secret key,
debug rejimi) **kodning ichiga yozish mumkin emas** — bu xavfsizlik
xatosi va Git'ga tasodifan push qilinib ketishi mumkin.

```env
# .env
APP_NAME=Storely API
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/storely_db
SECRET_KEY=juda-maxfiy-kalit-bu-yerda
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Django tajribangiz bilan solishtirish:** Siz allaqachon `django-environ`
va `python-decouple` bilan xuddi shu maqsadda ishlagansiz (`requirements.txt`
tarixingizda ko'rindi). FastAPI'da bu vazifani **Pydantic Settings**
(`pydantic-settings`) bajaradi — bu ancha kuchli, chunki validatsiya
bilan birga keladi.

## 4. `.gitignore`ga `.env` qo'shish — MUHIM!

.gitignore
.env
venv/
pycache/

**Hech qachon** `.env` faylni Git'ga qo'shmang — bu yerda parollar,
API kalitlar bo'ladi. Buning o'rniga **`.env.example`** yarating —
bu maxfiy qiymatlarsiz, faqat qaysi o'zgaruvchilar kerakligini
ko'rsatadigan namuna fayl, u Git'ga qo'shiladi:

```env
# .env.example
APP_NAME=Storely API
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Bu — boshqa developer (yoki siz kelajakda) loyihani clone qilganda,
qanday `.env` yaratish kerakligini bilishi uchun.

## 5. `BaseSettings` — Pydantic orqali `.env`ni o'qish

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "My API"
    debug: bool = False
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30


settings = Settings()
```

**Muhim xususiyatlar:**
- `Settings` — oddiy Pydantic model kabi ishlaydi, lekin qiymatlarni
  **avtomatik `.env` faylidan** o'qiydi
- Agar `.env`da `DATABASE_URL` bo'lmasa (va default qiymat berilmagan
  bo'lsa) — dastur ishga tushishi bilanoq **validatsiya xatosi** beradi
  (bu juda foydali — "unutilgan" konfiguratsiyani ishga tushmasdan oldin
  aniqlaysiz)
- Katta-kichik harf sezgir emas — `.env`da `DATABASE_URL` yozilgan
  bo'lsa ham, Python kodida `settings.database_url` (kichik harf,
  snake_case) ishlatiladi

## 6. `settings`ni ishlatish

```python
# app/main.py
from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/config-info")
def config_info():
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        # SECRET_KEY hech qachon response'da ko'rsatilmaydi!
    }
```

## 7. Muhitlar (environments) — development, staging, production

Katta loyihalarda ko'pincha bir nechta `.env` fayli bo'ladi:

.env.development
.env.staging
.env.production

Va ishga tushirishda qaysi birini ishlatishni tanlash mumkin:

```python
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = f".env.{os.getenv('ENVIRONMENT', 'development')}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file)
    ...
```

Hozircha loyihalaringiz uchun bitta `.env` yetarli, lekin bu naqshni
bilib qo'yish keyinchalik (Render/Railway'ga deploy qilishda) foydali
bo'ladi.

## 8. `lru_cache` bilan Settings'ni optimallashtirish

`Settings()` har safar chaqirilganda `.env` faylini qayta o'qimasligi
uchun, ko'pincha `functools.lru_cache` bilan keshlab qo'yiladi:

```python
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My API"
    database_url: str
    secret_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Keyin dependency sifatida ishlatiladi (Dars 07'ni eslang!):

```python
from fastapi import Depends

@app.get("/info")
def info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name}
```

Bu naqsh — Dars 12'dan boshlab DB connection bilan ham xuddi shunday
ishlatiladi (`get_db()` dependency orqali).

## 9. Nested Settings — guruhlangan sozlamalar

Katta loyihalarda sozlamalarni guruhlash mumkin:

```python
class DatabaseSettings(BaseSettings):
    url: str
    pool_size: int = 5


class Settings(BaseSettings):
    app_name: str = "My API"
    database: DatabaseSettings = DatabaseSettings()
```

Hozircha loyihalaringiz uchun bu darajada murakkablik shart emas, lekin
professional loyihalarda (Delivery API'da) buni ko'rishingiz mumkin.

## Xulosa

- **`app/` paket strukturasi** — routerlar, config, database, models
  alohida fayllarga bo'lingan, katta loyiha uchun standart
- **`.env`** — maxfiy va muhitga bog'liq qiymatlar, **hech qachon
  Git'ga qo'shilmaydi**
- **`.env.example`** — namuna fayl, Git'ga qo'shiladi
- **`BaseSettings`** (pydantic-settings) — `.env`ni avtomatik o'qiydigan,
  validatsiya qiluvchi klass
- **`lru_cache`** — Settings obyektini bir marta yaratib, qayta
  ishlatish uchun
- Bu struktura — Dars 12 (Database), Dars 19-22 (Authentication) va
  ayniqsa Dars 23 (Service Layer) uchun **poydevor**


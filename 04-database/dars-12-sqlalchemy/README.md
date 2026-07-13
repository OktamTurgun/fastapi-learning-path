# Dars 12 — SQLAlchemy, Engine, Session

Bu — 4-modulning birinchi darsi va butun kursning eng katta burilish
nuqtalaridan biri: shu yerdan boshlab statik `list`/`dict` o'rniga
**haqiqiy ma'lumotlar bazasi** bilan ishlaysiz.

## 1. SQLAlchemy nima?

**SQLAlchemy** — Python uchun eng mashhur **ORM** (Object-Relational
Mapper). ORM — Python klasslari orqali SQL jadvallar bilan ishlash
imkonini beradi, siz to'g'ridan-to'g'ri SQL yozmaysiz (garchi zarur
bo'lsa yozish imkoniyati ham bor).

**Django DRF bilan solishtirish:** Bu — aynan **Django ORM**ning
o'rnini bosadi. Farqi:

| | Django ORM | SQLAlchemy |
|---|---|---|
| Integratsiya | Django bilan chambarchas bog'liq | Har qanday Python loyihasida ishlatiladi |
| Sintaksis | `Model.objects.filter(...)` | `session.query(Model).filter(...)` (yoki yangi `select()`) |
| Migratsiya | Built-in (`makemigrations`, `migrate`) | Alohida kutubxona — **Alembic** (Dars 14) |
| Moslashuvchanlik | Cheklangan (Django konventsiyasiga bog'liq) | Juda moslashuvchan, "explicit is better than implicit" |

## 2. Asosiy 3 ta tushuncha

SQLAlchemy bilan ishlash uchun 3 ta asosiy tushunchani bilish kerak:

1. **Engine** — ma'lumotlar bazasiga ulanish "manzili" va sozlamalari
2. **Session** — bitta "suhbat" (transaction) davomida DB bilan ishlash
   uchun vosita
3. **Model (Base)** — Python klassi orqali jadval strukturasini
   belgilash (Dars 13'da chuqurroq)

## 3. Engine yaratish

```python
from sqlalchemy import create_engine

# SQLite uchun (fayl asosida, o'rganish uchun qulay)
DATABASE_URL = "sqlite:///./storely.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # faqat SQLite uchun kerak
)
```

**PostgreSQL uchun** (real loyihalaringizda ishlatilgan format):
```python
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
engine = create_engine(DATABASE_URL)
```

`connect_args={"check_same_thread": False}` — bu **faqat SQLite**
uchun kerak, chunki SQLite standart holatda bitta so'rov bitta thread
bilan cheklangan, FastAPI esa turli thread'larda ishlashi mumkin.
PostgreSQL/MySQL bilan bu parametr kerak emas.

## 4. `Base` — barcha model klasslarining ota-klassi

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

Dars 13'da barcha jadval modellaringiz (`User`, `Product`, `Order`)
shu `Base`dan meros oladi:

```python
class User(Base):
    __tablename__ = "users"
    # ... maydonlar Dars 13'da
```

## 5. `SessionLocal` — Session yaratuvchi fabrika

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- `autocommit=False` — har bir amal avtomatik saqlanmaydi, siz
  `.commit()` chaqirmaguningizcha o'zgarishlar vaqtinchalik turadi
  (bu — xavfsizroq, chunki xato yuz bersa, `.rollback()` bilan bekor
  qilish mumkin)
- `autoflush=False` — so'rovlar avtomatik "flush" qilinmaydi (bu
  performance uchun ko'proq nazorat beradi)
- `bind=engine` — bu session qaysi Engine orqali ishlashini bildiradi

## 6. `get_db()` — Dependency Injection bilan Session (Dars 07'ni eslang!)

Bu — Dars 07'da o'rgangan **`yield` bilan dependency** naqshining eng
muhim amaliy qo'llanilishi:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `yield`dan oldin — session ochiladi
- `yield db` — bu yerda FastAPI endpoint funksiyasi ishga tushadi,
  `db` obyekti unga beriladi
- `finally: db.close()` — endpoint tugagach (xato bo'lsa ham),
  session **albatta** yopiladi — bu resurs oqishining (connection leak)
  oldini oladi

## 7. Bu `get_db()`ni endpoint'da qanday ishlatish (oldindan ko'rish)

```python
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    # db orqali so'rovlar yozamiz (Dars 15'da CRUD bilan chuqurroq)
    return {"message": "DB session tayyor"}
```

Har bir so'rov o'zining **alohida** Session'ini oladi, so'rov tugagach
avtomatik yopiladi — bu Django'dagi `request`ning avtomatik DB connection
boshqaruviga o'xshaydi, lekin FastAPI'da buni **siz o'zingiz** dependency
orqali qurasiz.

## 8. Connection Pool haqida qisqacha

SQLAlchemy Engine ichida **connection pool** boshqaradi — bu degani,
har bir so'rov uchun yangi DB ulanish ochish o'rniga, oldindan tayyorlab
qo'yilgan ulanishlar "pool"idan foydalanadi. Bu ayniqsa production'da
(PostgreSQL bilan) muhim — performance uchun.

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # doimiy ochiq ulanishlar soni
    max_overflow=10,       # qo'shimcha vaqtinchalik ulanishlar
)
```

Hozircha SQLite bilan bu parametrlar unchalik muhim emas, lekin
Storely yoki EduCore CRM kabi PostgreSQL loyihalarida bu sozlamalar
performance'ga sezilarli ta'sir qiladi.

## 9. To'liq `database.py` namunasi

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./storely.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Bu fayl — Dars 13'dan boshlab **har bir loyihada** deyarli o'zgarishsiz
qayta ishlatiladigan standart shablon bo'ladi.

## Xulosa

- **Engine** — DB'ga ulanish sozlamalari (`create_engine`)
- **Base** — barcha model klasslarining ota-klassi (`declarative_base`)
- **SessionLocal** — har bir so'rov uchun yangi Session yaratadigan
  fabrika (`sessionmaker`)
- **`get_db()`** — Dars 07'dagi `yield` dependency naqshi orqali
  Session'ni ochib, ishlatib, avtomatik yopish
- SQLite — o'rganish uchun qulay, PostgreSQL — production uchun (faqat
  `DATABASE_URL` va `connect_args` o'zgaradi, qolgan kod bir xil qoladi)
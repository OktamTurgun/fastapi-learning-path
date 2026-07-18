# FastAPI Learning Path 🚀

FastAPI'ni noldan professional darajagacha o'rganish uchun tuzilgan
shaxsiy o'quv yo'lim. Django/DRF fonida backend developer sifatida,
FastAPI'ni chuqur va amaliy tarzda o'zlashtirish maqsadida yaratilgan.

## 🛠 Tech Stack

- **Til:** Python 3.13
- **Framework:** FastAPI
- **Validation:** Pydantic v2
- **Database:** PostgreSQL + SQLAlchemy + Alembic
- **Auth:** JWT (python-jose / passlib)
- **Testing:** pytest + TestClient
- **DevOps:** Docker, Docker Compose, GitHub Actions (CI/CD)
- **Deployment:** Render / Railway

## 📚 Kurs strukturasi

Har bir dars alohida papkada joylashgan: `README.md` (nazariya),
`main.py` (kod misoli), `exercise.py` (mustaqil mashq).

### ✅ Progress

- [x] **01 — Fundamentals**
  - [x] Dars 01 — FastAPI nima?
  - [x] Dars 02 — ASGI va WSGI nima?
  - [x] Dars 03 — Project yaratish
  - [x] Dars 04 — Routing
  - [x] Dars 05 — HTTP Methods
  - [x] Dars 06 — Path & Query Parameters
  - [x] Dars 07 — Dependency Injection
- [x] **02 — Pydantic**
  - [x] Dars 08 — BaseModel
  - [x] Dars 09 — Nested Models
  - [x] Dars 10 — Response Model
- [x] **03 — Project Setup**
  - [x] Dars 11 — Config & Structure
- [x] **04 — Database**
  - [x] Dars 12 — SQLAlchemy
  - [x] Dars 13 — ORM Models & Relationships
  - [x] Dars 14 — Alembic
  - [x] Dars 15 — CRUD
  - [ ] Dars 16 — Pagination & Filtering
  - [ ] Dars 17 — Async SQLAlchemy
- [ ] **05 — Testing Basics**
  - [ ] Dars 18 — pytest & TestClient
- [ ] **06 — Authentication**
  - [ ] Dars 19 — Password Hashing
  - [ ] Dars 20 — JWT
  - [ ] Dars 21 — Protected Routes
  - [ ] Dars 22 — Exception Handling & CORS
- [ ] **07 — Architecture**
  - [ ] Dars 23 — Service Layer
  - [ ] Dars 24 — Repository Pattern
  - [ ] Dars 25 — Permissions & Roles
- [ ] **08 — Professional Layer**
  - [ ] Dars 26 — Background Tasks, Redis, Celery
  - [ ] Dars 27 — Docker
  - [ ] Dars 28 — Deployment
- [ ] **09 — Delivery API** (katta amaliy loyiha)
- [ ] **10 — Debt Monitoring System** (yakuniy loyiha)

## ⚙️ O'rnatish

```bash
git clone git@github.com:OktamTurgun/fastapi-learning-path.git
cd fastapi-learning-path

python -m venv venv
venv\Scripts\activate          # Windows PowerShell

pip install -r requirements.txt
```

## ▶️ Har bir darsni ishga tushirish

```bash
cd 01-fundamentals/dars-01-fastapi-nima
uvicorn main:app --reload
```

Keyin brauzerda:
- `http://127.0.0.1:8000/docs` — Swagger UI
- `http://127.0.0.1:8000/redoc` — ReDoc

## 📝 Git Workflow

```bash
git add .
git commit -m "docs(dars-XX): qisqa tavsif"
git push
```

Conventional commits ishlatiladi: `docs`, `feat`, `fix`, `chore`, `refactor`.

## 📄 License

Bu loyiha [MIT License](LICENSE) ostida tarqatiladi.

## 👤 Muallif

**Uktam** — Junior Backend Developer (Python/Django/DRF), 42.uz talabasi
GitHub: [@OktamTurgun](https://github.com/OktamTurgun)
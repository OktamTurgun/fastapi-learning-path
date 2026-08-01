# =============================================================================
# Dars-22: Exception Handling testlari
# Bu faylda uchta asosiy exception handler sinovdan o'tkaziladi:
#   1. validation_exception_handler  — 422 Pydantic xatolari
#   2. generic_exception_handler     — 500 kutilmagan xatolar
#   3. HTTPException handler         — 404 / 400 / 401 xatolari
# =============================================================================


# -----------------------------------------------------------------------------
# 1. VALIDATSIYA XATOLARI (422) — validation_exception_handler
# -----------------------------------------------------------------------------

def test_validation_error_missing_required_field(client):
    """
    Mahsulot yaratishda majburiy maydon (name) yuborilmasa,
    422 qaytishi va 'errors' massivi bo'lishi kerak.
    """
    response = client.post("/categories/", json={})   # 'name' yo'q
    assert response.status_code == 422
    body = response.json()
    # Bizning custom handler "detail" va "errors" qaytaradi
    assert body["detail"] == "Validatsiya xatosi"
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) > 0


def test_validation_error_contains_field_and_message(client):
    """
    'errors' massividagi har bir element 'field' va 'message' kalitlariga ega bo'lishi kerak.
    """
    response = client.post("/categories/", json={})
    body = response.json()
    first_error = body["errors"][0]
    assert "field" in first_error
    assert "message" in first_error


def test_validation_error_wrong_type(client):
    """
    Noto'g'ri tip yuborilganda (price string o'rniga harf) 422 qaytishi kerak.
    """
    # Kategoriya yaratib olamiz
    cat = client.post("/categories/", json={"name": "Test"})
    cat_id = cat.json()["id"]

    # Foydalanuvchi ro'yxatdan o'tadi va token oladi
    client.post("/users/register", json={
        "email": "val_test@example.com",
        "password": "Parol123",
        "full_name": "Val Tester",
    })
    login = client.post("/users/login", json={
        "email": "val_test@example.com",
        "password": "Parol123",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post("/products/", json={
        "name": "Sichqoncha",
        "price": "narx_emas",   # float o'rniga string
        "category_id": cat_id,
    }, headers=headers)

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "Validatsiya xatosi"


def test_validation_error_negative_limit(client):
    """
    Query param chegarasidan chiqilganda (limit=-1) ham 422 qaytishi kerak.
    """
    response = client.get("/products/?limit=-1")
    assert response.status_code == 422
    assert response.json()["detail"] == "Validatsiya xatosi"


def test_validation_error_invalid_order_param(client):
    """
    'order' parametri pattern='^(asc|desc)$' bo'lishi kerak.
    Noto'g'ri qiymat yuborilsa 422 qaytishi kerak.
    """
    response = client.get("/products/?order=random")
    assert response.status_code == 422
    assert response.json()["detail"] == "Validatsiya xatosi"


# -----------------------------------------------------------------------------
# 2. HTTP 404 XATOLARI — HTTPException orqali
# -----------------------------------------------------------------------------

def test_404_product_not_found(client):
    """Mavjud bo'lmagan mahsulot ID so'ralganda 404 qaytishi kerak."""
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Mahsulot topilmadi"


def test_404_category_not_found(client):
    """Mavjud bo'lmagan kategoriya ID so'ralganda 404 qaytishi kerak."""
    response = client.get("/categories/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Kategoriya topilmadi"


def test_404_update_product_not_found(client):
    """Mavjud bo'lmagan mahsulotni yangilashga urinilganda 404 qaytishi kerak."""
    response = client.patch("/products/99999", json={"price": 50000})
    assert response.status_code == 404
    assert response.json()["detail"] == "Mahsulot topilmadi"


def test_404_update_category_not_found(client):
    """Mavjud bo'lmagan kategoriyani yangilashga urinilganda 404 qaytishi kerak."""
    response = client.patch("/categories/99999", json={"name": "Yangi nom"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Kategoriya topilmadi"


def test_404_delete_product_not_found(client):
    """Mavjud bo'lmagan mahsulotni o'chirishga urinilganda 404 qaytishi kerak."""
    response = client.delete("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Mahsulot topilmadi"


def test_404_delete_category_not_found(client):
    """Mavjud bo'lmagan kategoriyani o'chirishga urinilganda 404 qaytishi kerak."""
    response = client.delete("/categories/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Kategoriya topilmadi"


# -----------------------------------------------------------------------------
# 3. HTTP 400 XATOLARI — Takroriy ma'lumot
# -----------------------------------------------------------------------------

def test_400_duplicate_email_registration(client):
    """
    Bir xil email bilan ikki marta ro'yxatdan o'tishga urinilganda
    400 qaytishi va xato xabari bo'lishi kerak.
    """
    payload = {
        "email": "duplicate@example.com",
        "password": "Parol123",
        "full_name": "Duplicate User",
    }
    # Birinchi marta — muvaffaqiyatli
    r1 = client.post("/users/register", json=payload)
    assert r1.status_code == 201

    # Ikkinchi marta — xato
    r2 = client.post("/users/register", json=payload)
    assert r2.status_code == 400
    assert r2.json()["detail"] == "Bu email allaqachon ro'yxatdan o'tgan"


# -----------------------------------------------------------------------------
# 4. HTTP 401 XATOLARI — Autentifikatsiya xatolari
# -----------------------------------------------------------------------------

def test_401_wrong_password(client):
    """Noto'g'ri parol bilan login qilinganda 401 qaytishi kerak."""
    client.post("/users/register", json={
        "email": "authtest@example.com",
        "password": "TogrParol123",
        "full_name": "Auth Tester",
    })
    response = client.post("/users/login", json={
        "email": "authtest@example.com",
        "password": "XatoParol999",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


def test_401_wrong_email(client):
    """Mavjud bo'lmagan email bilan login qilinganda 401 qaytishi kerak."""
    response = client.post("/users/login", json={
        "email": "yoq@example.com",
        "password": "AnyParol123",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


def test_401_no_token_on_protected_route(client):
    """
    Token berilmasdan himoyalangan endpoint chaqirilganda
    401 qaytishi kerak.
    """
    cat = client.post("/categories/", json={"name": "Test"})
    cat_id = cat.json()["id"]

    response = client.post("/products/", json={
        "name": "Mahsulot",
        "price": 10000,
        "category_id": cat_id,
    })
    # Token yo'q — 401 yoki 403 qaytishi kerak
    assert response.status_code in (401, 403)


def test_401_invalid_token(client):
    """
    Noto'g'ri (yaroqsiz) token bilan himoyalangan endpoint chaqirilganda
    401 qaytishi kerak.
    """
    cat = client.post("/categories/", json={"name": "Test"})
    cat_id = cat.json()["id"]

    response = client.post("/products/", json={
        "name": "Mahsulot",
        "price": 10000,
        "category_id": cat_id,
    }, headers={"Authorization": "Bearer bu.token.xato"})
    assert response.status_code == 401


# -----------------------------------------------------------------------------
# 5. JAVOB FORMATI tekshiruvi
# -----------------------------------------------------------------------------

def test_error_response_is_json(client):
    """Barcha xato javoblari JSON formatida bo'lishi kerak."""
    response = client.get("/products/99999")
    # Content-Type JSON ekanligini tekshirish
    assert "application/json" in response.headers["content-type"]
    # JSON parse bo'lishi kerak (exception bo'lmaydi)
    body = response.json()
    assert "detail" in body


def test_validation_error_response_structure(client):
    """
    Validatsiya xatosi javobi aniq strukturaga ega bo'lishi kerak:
    { "detail": "Validatsiya xatosi", "errors": [...] }
    """
    response = client.post("/categories/", json={})
    body = response.json()

    assert "detail" in body
    assert "errors" in body
    assert body["detail"] == "Validatsiya xatosi"
    assert isinstance(body["errors"], list)


def test_404_response_has_detail_key(client):
    """404 xato javobi 'detail' kalitiga ega bo'lishi kerak."""
    response = client.get("/products/99999")
    assert "detail" in response.json()


def test_400_response_has_detail_key(client):
    """400 xato javobi 'detail' kalitiga ega bo'lishi kerak."""
    payload = {"email": "fmt@example.com", "password": "Parol123", "full_name": "Test"}
    client.post("/users/register", json=payload)
    response = client.post("/users/register", json=payload)
    assert "detail" in response.json()

"""
Users bilan bog'liq barcha endpointlar shu yerda joylashadi.
Bu fayl "prefix" haqida bilmaydi — uni kim ulashi (main.py)
shuni hal qiladi. Shu sababli bu router boshqa loyihada ham
qayta ishlatilishi mumkin.
"""

from fastapi import APIRouter

router = APIRouter()

# Statik demo ma'lumot (Dars 15'da bu DB'dan keladi)
fake_users = [
    {"id": 1, "ism": "Olim", "rol": "developer"},
    {"id": 2, "ism": "Aziza", "rol": "designer"},
]


@router.get("/")
def list_users():
    """Barcha foydalanuvchilar ro'yxati."""
    return {"users": fake_users}


@router.get("/{user_id}")
def get_user(user_id: int):
    """Bitta foydalanuvchini id orqali topish."""
    for user in fake_users:
        if user["id"] == user_id:
            return user
    return {"xato": "Foydalanuvchi topilmadi"}
    
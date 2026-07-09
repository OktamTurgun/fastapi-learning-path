"""
Dars 09 — Mustaqil mashq: Theater Manager — Spektakl bron qilish tizimi

Vazifa:

1. `Actor` modelini yarating:
   - name: str, min_length=2
   - role: str  (masalan "asosiy qahramon")

2. `Performance` modelini yarating:
   - title: str, min_length=2
   - actors: List[Actor]   (bir nechta aktyor)
   - duration_minutes: int, gt=0

3. `Spectator` (tomoshabin) modelini yarating:
   - full_name: str, min_length=2
   - email: EmailStr
   - phone: Optional[str] = None

4. `Booking` (bron) modelini yarating:
   - spectator: Spectator
   - performance: Performance
   - seat_numbers: List[int]   (masalan [5, 6, 7])

   Bonus metod qo'shing: `total_seats()` — seat_numbers uzunligini qaytarsin.

5. In-memory bookings_db va next_id yarating.

6. POST "/bookings" — Booking modelini qabul qilib, yangi bron yaratsin,
   status_code=201. Javobda total_seats ham ko'rsatilsin.

7. GET "/bookings" — barcha bronlarni qaytarsin.

8. GET "/bookings/{booking_id}" — bitta bronni qaytarsin, 404 bilan.

Test uchun JSON:
{
  "spectator": {
    "full_name": "Malika Yusupova",
    "email": "malika@example.com",
    "phone": "+998901234567"
  },
  "performance": {
    "title": "Pinokkio",
    "actors": [
      {"name": "Aziz", "role": "Pinokkio"},
      {"name": "Nodira", "role": "Fея"}
    ],
    "duration_minutes": 60
  },
  "seat_numbers": [5, 6, 7]
}

Bonus: agar email noto'g'ri formatda yuborilsa, 422 xato chiqishini
tasdiqlang.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, Field

app = FastAPI(title="Theater Booking API", version="1.0.0")


# TODO: Actor modelini yarating
class Actor(BaseModel):
  name: str = Field(..., min_length=2)
  role: str = Field(..., min_length=2)


# TODO: Performance modelini yarating (actors: List[Actor])
class Performance(BaseModel):
  title: str = Field(..., min_length=2)
  actors: List[Actor]
  duration_minutes: int = Field(..., gt=0)



# TODO: Spectator modelini yarating (email: EmailStr)
class Spectator(BaseModel):
  full_name: str = Field(..., min_length=2)
  email: EmailStr
  phone: Optional[str] = None


class Booking(BaseModel):
    spectator: Spectator
    performance: Performance
    seat_numbers: List[int]

    @field_validator("seat_numbers")
    @classmethod
    def validate_seats(cls, v):
        if any(seat <= 0 for seat in v):
            raise ValueError("Seat raqamlari musbat bo'lishi kerak")
        return v

    def total_seats(self) -> int:
        return len(self.seat_numbers)
  
booking_db: List[dict] = []
next_id: int = 1


@app.post("/bookings", status_code=status.HTTP_201_CREATED, tags=["Booking"])
def create_booking(booking: Booking):
    global next_id
    new_booking = {
        "id": next_id,
        "spectator": booking.spectator.model_dump(),
        "performance": booking.performance.model_dump(),
        "seat_numbers": booking.seat_numbers,
        "total_seats": booking.total_seats(),
    }
    booking_db.append(new_booking)
    next_id += 1
    return new_booking


@app.get("/bookings", tags=["Bookings"])
def list_bookings():
    return {"bookings": booking_db}


@app.get("/bookings/{booking_id}", tags=["Bookings"])
def get_booking(booking_id: int):
    for booking in booking_db:
        if booking["id"] == booking_id:
            return booking
    raise HTTPException(status_code=404, detail="Bron topilmadi")

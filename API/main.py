from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import SessionLocal, engine

app = FastAPI()

# Zależność do pobierania sesji bazy danych
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD OPERATIONS ---

# 1. CREATE (Dodawanie rekordu)
@app.post("/cars/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = models.VintageCar(
        marka_model=car.marka_model,
        rok_produkcji=car.rok_produkcji,
        czy_na_chodzie=car.czy_na_chodzie
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# 2. READ (Odczyt wszystkich rekordów)
@app.get("/cars/", response_model=List[schemas.Car])
def read_cars(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
   cars = db.query(models.VintageCar).order_by(models.VintageCar.id).offset(skip).limit(limit).all()
   return cars

# 3. READ (Odczyt jednego rekordu po ID)
@app.get("/cars/{car_id}", response_model=schemas.Car)
def read_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

# 4. UPDATE (Zmiana rekordu)
@app.put("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car_update: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    db_car.marka_model = car_update.marka_model
    db_car.rok_produkcji = car_update.rok_produkcji
    db_car.czy_na_chodzie = car_update.czy_na_chodzie
    
    db.commit()
    db.refresh(db_car)
    return db_car

# 5. DELETE (Usunięcie rekordu)
@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    db.delete(db_car)
    db.commit()
    return {"message": "Car deleted successfully"}
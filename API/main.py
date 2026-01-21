import time
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import SessionLocal, engine

# Tworzenie tabel
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS (Niezbędne, aby React widział API) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Porty Reacta
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- CRUD ---

# 1. CREATE + Walidacja dla formularza (Wymóg 3/4)
@app.post("/cars/", response_model=schemas.Car)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)):
    # Symulacja błędu biznesowego nieobsłużonego przez frontend
    time.sleep(1) # <--- OPÓŹNIENIE 1 SEKUNDA
    if car.rok_produkcji < 1900:
        raise HTTPException(status_code=400, detail="Rok produkcji musi być wyższy niż 1900.")
        
    db_car = models.VintageCar(
        marka_model=car.marka_model,
        rok_produkcji=car.rok_produkcji,
        czy_na_chodzie=car.czy_na_chodzie
    )
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car

# 2. READ + Filtrowanie (Wymóg 7)
@app.get("/cars/", response_model=List[schemas.Car])
def read_cars(
    skip: int = 0, 
    limit: int = 100, 
    filter_type: Optional[str] = Query("all"), # all, true, false
    db: Session = Depends(get_db)
):
    query = db.query(models.VintageCar)
    
    # Logika filtrowania po stronie API
    if filter_type == "true":
        query = query.filter(models.VintageCar.czy_na_chodzie == True)
    elif filter_type == "false":
        query = query.filter(models.VintageCar.czy_na_chodzie == False)
        
    cars = query.order_by(models.VintageCar.id).offset(skip).limit(limit).all()
    return cars

# 3. READ ONE
@app.get("/cars/{car_id}", response_model=schemas.Car)
def read_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

# 4. UPDATE + Walidacja (Wymóg 3/4)
@app.put("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_id: int, car_update: schemas.CarCreate, db: Session = Depends(get_db)):
    db_car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    if car_update.rok_produkcji < 1900:
        raise HTTPException(status_code=400, detail="Rok produkcji musi być wyższy niż 1900.")
    
    db_car.marka_model = car_update.marka_model
    db_car.rok_produkcji = car_update.rok_produkcji
    db_car.czy_na_chodzie = car_update.czy_na_chodzie
    
    db.commit()
    db.refresh(db_car)
    return db_car

# 5. DELETE + Blokada logiczna (Wymóg 8b)
@app.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    db_car = db.query(models.VintageCar).filter(models.VintageCar.id == car_id).first()
    if db_car is None:
        raise HTTPException(status_code=404, detail="Car not found")
    
    # Blokada usuwania aut "nie na chodzie" dla demonstracji błędu
    if db_car.czy_na_chodzie == False:
        raise HTTPException(status_code=400, detail="Nie można usunąć auta, które nie jest na chodzie.")
    
    db.delete(db_car)
    db.commit()
    return {"message": "Deleted"}